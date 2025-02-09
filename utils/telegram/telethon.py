from __future__ import annotations

import asyncio
from typing import Optional, List
import os
from os.path import join
from dataclasses import dataclass, asdict
from itertools import cycle
import json

from data import config
from utils.core import logger
from utils.proxy import to_telethon, get_dataimpulse_proxy_by_phone
from urllib.parse import unquote
from .base import AccountInterface, AuthError
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.raw import types
import base64
import struct
import io
from stream_sqlite import stream_sqlite
from .telegram_settings import TelegramAccountSettings

def auth_session(
    session_file: "io.BytesIO",
    settings: "TelegramAccountSettings",
) -> str | None:
    auth_key, dc_id = None, None

    for table_name, _, rows in stream_sqlite(session_file, max_buffer_size=1_048_576):
        if table_name == "sessions":
            for row in rows:
                if (
                    all(hasattr(row, attr) for attr in ["auth_key", "dc_id"])
                    and row.auth_key is not None
                    and row.dc_id is not None
                ):
                    auth_key, dc_id = row.auth_key, row.dc_id
                    break

    if None in (auth_key, dc_id):
        return None

    return (
        base64.urlsafe_b64encode(
            struct.pack(
                ">BI?256sQ?",
                dc_id,
                settings.app_id,
                False,
                auth_key,
                999999999,
                False,
            )
        )
        .decode()
        .rstrip("=")
    )


def base64_original_length(session):
    padding = len(
        list(filter(lambda c: c == '\n' or c == '\r' or c == '=', session)))
    return int((3 * (len(session) / 4)) - padding)

def unpack_gramjs_session(session_string, web=True):
    session_string = session_string[1:]
    if web:
        server_length = base64_original_length(session_string) - 261
        dc_id, server_address_length, server_address, port, auth_key = struct.unpack(
            ">BH{}sH256s".format(server_length),
            base64.urlsafe_b64decode(session_string)
        )
    else:
        # Same as Telethon
        server_length = 4 if len(session_string) == 352 else 16
        dc_id, server_address, port, auth_key = struct.unpack(
            ">B{}sH256s".format(server_length),
            base64.urlsafe_b64decode(session_string)
        )

    return dc_id, server_address, port, auth_key


def unpack_telethon_session(session_string):
    return unpack_gramjs_session(session_string, False)

def telethon_to_pyrogram(telethon_session, tg_id, bot, api_id, test_mode=False):
    dc_id, _, _, auth_key = unpack_telethon_session(telethon_session)
    packed = struct.pack(
        ">BI?256sQ?",
        dc_id,
        api_id,
        test_mode,
        auth_key,
        tg_id,
        bot
    )
    return base64.urlsafe_b64encode(packed).decode().rstrip("=")
@dataclass
class TelethonParams:
    session: str
    api_id: int
    api_hash: str
    device_model: str
    system_version: str
    app_version: str
    lang_code: str
    system_lang_code: str


class TelethonAccount(AccountInterface):
    def __init__(
            self,
            session_file: Optional[str] = None,
            session_params: Optional[TelethonParams] = None,
            proxy: Optional[str] = None
    ):
        self.telegram_name = None
        self.proxy = proxy
        if session_file is not None:
            self.client = TelegramClient(
                session=session_file,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                proxy=to_telethon(proxy))
            self.name = session_file
        elif session_params is not None:
            self.client = TelegramClient(
                **asdict(session_params),
                proxy=to_telethon(proxy))
            self.name = session_params.session
        else:
            raise ValueError("Either session_file or session_params must be provided")
        if isinstance(self.name, StringSession):
            self.name = self.name.save()

    def get_proxy(self) -> Optional[str]:
        return self.proxy

    async def us3r(self, referral_code: Optional[str] = None):
        try:
            if isinstance(self.client.session, StringSession):
                await self.client.start()
                me = await self.client.get_me()
                meid=me.first
                await self.client.disconnect()
                self.str_sess1 = self.client.session.save()
                self.str_sess2 = telethon_to_pyrogram(self.str_sess1,meid,False,config.API_ID)

            else:
                session_file = io.BytesIO(open(self.client.session.filename, "rb").read())
                settings = TelegramAccountSettings(app_id=config.API_ID, app_hash=config.API_HASH,
                                                   sdk="SDK", app_version="1.0", device="Device")

                self.str_sess2 = auth_session(session_file, settings)
            async with Client(":memory:", api_id=config.API_ID, api_hash=config.API_HASH,
                              session_string=self.str_sess2) as app:
                me=await app.get_me()
                return f'{me.first_name} {me.last_name}'
        except Exception as e:
            raise AuthError(f"Failed to connect: {e}")


    async def get_tg_web_data(self, referral_code: Optional[str] = None):
        try:
            if isinstance(self.client.session, StringSession):
                await self.client.start()
                me = await self.client.get_me()
                meid=me.id
                await self.client.disconnect()
                self.str_sess1 = self.client.session.save()
                self.str_sess2 = telethon_to_pyrogram(self.str_sess1,meid,False,config.API_ID)

            else:
                session_file = io.BytesIO(open(self.client.session.filename, "rb").read())
                settings = TelegramAccountSettings(app_id=config.API_ID, app_hash=config.API_HASH,
                                                   sdk="SDK", app_version="1.0", device="Device")

                self.str_sess2 = auth_session(session_file, settings)

            async with Client(":memory:", api_id=config.API_ID, api_hash=config.API_HASH,
                              session_string=self.str_sess2) as app:
                peer = await app.resolve_peer('TheRokoBot')
                theme_params = "{\"accent_text_color\":\"#6ab2f2\",\"bg_color\":\"#17212b\",\"bottom_bar_bg_color\":\"#17212b\",\"button_color\":\"#5288c1\",\"button_text_color\":\"#ffffff\",\"destructive_text_color\":\"#ec3942\",\"header_bg_color\":\"#17212b\",\"hint_color\":\"#708499\",\"link_color\":\"#6ab3f3\",\"secondary_bg_color\":\"#232e3c\",\"section_bg_color\":\"#17212b\",\"section_header_text_color\":\"#6ab3f3\",\"section_separator_color\":\"#111921\",\"subtitle_text_color\":\"#708499\",\"text_color\":\"#f5f5f5\"}"
                web_view = await app.invoke(functions.messages.RequestWebView(
                    peer=types.InputPeerUser(
                        user_id=peer.user_id,
                        access_hash=peer.access_hash
                    ),
                    bot=types.InputUser(
                        user_id=peer.user_id,
                        access_hash=peer.access_hash
                    ),
                    url='https://api.roko.love/',
                    start_param='',
                    theme_params=types.DataJSON(data=theme_params),
                    platform='android'
                ))
        except Exception as e:
            raise AuthError(f"Failed to connect: {e}")

        await self.client.disconnect()
        return unquote(
            string=unquote(string=web_view.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

    @staticmethod
    def get_accounts(
            folder_path: str,
            proxies: Optional[List[str]] = None
    ) -> List[TelethonAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".session"):
                session = file.replace(".session", "")
                accounts.append(
                    TelethonAccount(session_file=join(folder_path, session), proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} telethon accounts")
        return accounts

    @staticmethod
    def json_to_params(
            json_data: dict,
            path_prefix: Optional[str] = None
    ) -> TelethonParams:
        if path_prefix:
            session = join(path_prefix, json_data['session_file'])
        else:
            session = json_data['session_file']
        return TelethonParams(
            session=session,
            api_id=json_data['app_id'],
            api_hash=json_data['app_hash'],
            device_model=json_data['device'],
            system_version=json_data['sdk'],
            app_version=json_data['app_version'],
            lang_code=json_data.get('lang_pack') or json_data.get('lang_code'),
            system_lang_code=json_data.get('system_lang_pack') or json_data.get('system_lang_code'),
        )

    @staticmethod
    def get_accounts_from_json_files(
            folder_path: str,
            proxies: Optional[List[str]] = None
    ) -> List[TelethonAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                with open(join(folder_path, file), 'r') as f:
                    session_params = TelethonAccount.json_to_params(json.load(f), path_prefix=folder_path)

                accounts.append(
                    TelethonAccount(session_params=session_params, proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} telethon account")
        return accounts

    @staticmethod
    def get_accounts_from_json_files(
            folder_path: str,
            proxies: Optional[List[str]] = None
    ) -> List[TelethonAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                with open(join(folder_path, file), 'r') as f:
                    session_params = TelethonAccount.json_to_params(json.load(f), path_prefix=folder_path)

                accounts.append(
                    TelethonAccount(session_params=session_params, proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} telethon accounts")
        return accounts

    @staticmethod
    def get_accounts_from_json_files_dataimpulse(
            folder_path: str
    ) -> List[TelethonAccount]:
        accounts = []
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                with open(join(folder_path, file), 'r') as f:
                    session_params = TelethonAccount.json_to_params(json.load(f), path_prefix=folder_path)

                accounts.append(
                    TelethonAccount(session_params=session_params,
                                    proxy=get_dataimpulse_proxy_by_phone(
                                        session_params.session.removesuffix('.session').removeprefix('sessions/')))
                )
        logger.info(f"Loaded {len(accounts)} telethon account")
        return accounts

    def __str__(self):
        return str(self.telegram_name or self.name)

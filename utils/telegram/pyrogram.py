from __future__ import annotations
from typing import Optional, List
import os
from os.path import join
from abc import ABC, abstractmethod
from itertools import cycle

from pyrogram import Client
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import functions
from pyrogram.raw import types
from data import config
from utils.core import logger
from utils.proxy import to_pyrogram
from urllib.parse import unquote
from .base import AccountInterface, AuthError



class PyrogramAccount(AccountInterface):
    def __init__(
            self, 
            name: str,
            proxy: Optional[str] = None
            ):
        self.name = name
        self.proxy = proxy
        self.telegram_name = None
        self.client = Client(
            name=name, 
            api_id=config.API_ID, 
            api_hash=config.API_HASH,
            proxy=to_pyrogram(proxy))
        
    def get_proxy(self) -> Optional[str]:
        return self.proxy

    async def us3r(self, referral_code: Optional[str] = None):
        """
        Get the Telegram web data needed for login.
        """
        try:
            await self.client.connect()
            me = await self.client.get_me()
            if not me:
                raise AuthError("Failed to get Telegram details")
            self.telegram_name = f'{me.first_name} {me.last_name}'
        except Exception as e:
            raise AuthError(f"Failed to connect: {e}")
        return self.telegram_name
    async def get_tg_web_data(self, referral_code: Optional[str] = None):
        """
        Get the Telegram web data needed for login.
        """
        try:
            await self.client.connect()
            me = await self.client.get_me()
            if not me:
                raise AuthError("Failed to get Telegram details")
            if me.username:
                self.telegram_name = f'@{me.username}'
            else:
                self.telegram_name = me.first_name
        except Exception as e:
            raise AuthError(f"Failed to connect: {e}")

        peer = await self.client.resolve_peer('TheRokoBot')
        theme_params = "{\"accent_text_color\":\"#6ab2f2\",\"bg_color\":\"#17212b\",\"bottom_bar_bg_color\":\"#17212b\",\"button_color\":\"#5288c1\",\"button_text_color\":\"#ffffff\",\"destructive_text_color\":\"#ec3942\",\"header_bg_color\":\"#17212b\",\"hint_color\":\"#708499\",\"link_color\":\"#6ab3f3\",\"secondary_bg_color\":\"#232e3c\",\"section_bg_color\":\"#17212b\",\"section_header_text_color\":\"#6ab3f3\",\"section_separator_color\":\"#111921\",\"subtitle_text_color\":\"#708499\",\"text_color\":\"#f5f5f5\"}"
        web_view = await self.client.invoke(functions.messages.RequestWebView(
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
            platform='tdesktop'
        ))
        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

    @staticmethod
    def get_accounts(
            folder_path: str, 
            proxies: Optional[List[str]] = None
            ) -> List[PyrogramAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".session"):
                session = file.replace(".session", "")
                accounts.append(
                    PyrogramAccount(name=join(folder_path, session), proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} pyrogram accounts")
        return accounts
    
    def __str__(self):
        return str(self.telegram_name or self.name)
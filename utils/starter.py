import asyncio
from asyncio import sleep, Semaphore
from random import uniform
from typing import Union
import random
import aiohttp
from aiohttp_proxy import ProxyConnector
import re
from .agents import generate_random_user_agent
from data import config
from utils.roko import rokoBot
from utils.core import logger
from utils.helper import format_duration
from utils.telegram import AccountInterface
from utils.proxy import to_url
import hashlib
from pyrogram.errors import (
    Unauthorized, UserDeactivated, AuthKeyUnregistered, UserDeactivatedBan,
    AuthKeyDuplicated, SessionExpired, SessionRevoked, FloodWait, UserAlreadyParticipant
)
from pyrogram.raw import types
from pyrogram.raw import functions
import json


try:
    from aiocfscrape import CloudflareScraper
    Session = CloudflareScraper
except:
    logger.info("Error when importing aiocfscrape.CloudflareScraper, using aiohttp.ClientSession instead")
    Session = aiohttp.ClientSession






async def bebe(roko,name_account):
    while True:
        await roko.check_items(name_account)
        await asyncio.sleep(900)

sem = Semaphore(config.ACCOUNT_PER_ONCE)
async def start(account: AccountInterface):
    sleep_dur = 0
    while True:
        await sleep(sleep_dur)
        async with sem:
            proxy = account.get_proxy()
            if proxy is None:
                connector = None
            else:
                connector = ProxyConnector.from_url(to_url(proxy))
            async with Session(headers={'User-Agent': generate_random_user_agent(device_type='android',
                                                                                        browser_type='chrome')},
                                        timeout=aiohttp.ClientTimeout(total=60), connector=connector) as session:
                try:
                    roko = rokoBot(account=account, session=session)
                    name_account=await account.us3r()
                    await sleep(uniform(*config.DELAYS['ACCOUNT']))
                    a=await roko.login()
                    logger.success(f"{name_account} |  Login Successful")
                    user_data= await roko.user_data(name_account)
                    if user_data['balance']>=4000:
                        auto_buy_box1 = await roko.auto_buy_box1(name_account)
                    if user_data['balance']>=100000:
                        auto_buy_box2 = await roko.auto_buy_box2(name_account)
                    task = asyncio.create_task(bebe(roko,name_account))
                    while True:
                        b = await roko.snake_game(name_account)
                        await asyncio.sleep(3)
                        user_data = await roko.user_data(name_account)
                        logger.success(
                            f"{name_account} | Snake Game +300 ROKO | balance: {user_data['balance']} ROKO")
                        if user_data['balance'] >= 4000:
                            auto_buy_box1 = await roko.auto_buy_box1(name_account)
                        if user_data['balance'] >= 100000:
                            auto_buy_box2 = await roko.auto_buy_box2(name_account)
                        await asyncio.sleep(30)

                except Exception as e:
                        logger.error(f"Error: {e}")
                except Exception as outer_e:
                    logger.error(f"Session error: {outer_e}")
        logger.info(f"Reconnecting in {format_duration(config.ITERATION_DURATION)}...")
        sleep_dur = config.ITERATION_DURATION


async def stats():
    logger.success("Analytics disabled")

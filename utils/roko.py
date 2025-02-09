import asyncio
import random
from utils.core import logger

from aiohttp import ClientSession
import aiohttp
import json
from data import config
from utils.core import logger
from utils.telegram import AccountInterface
import urllib.parse
def gen_xapi(lid=None, mid=None, appid=None):
    return f"{lid}:{mid}:{appid}:{str(random.random())}"
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Origin": "https://roko.love",
    "Referer": "https://roko.love",
}
def convert_to_url_encoded(data: str) -> str:

    parts = data.split('&')
    parsed_data = {}

    for part in parts:
        key, value = part.split('=', 1)
        if key == "user":
            parsed_data[key] = urllib.parse.quote(value)
        else:
            parsed_data[key] = value

    encoded_data = "&".join([f"{key}={value}" for key, value in parsed_data.items()])
    return encoded_data

class RefCodeError(Exception):
    pass

class AccountUsedError(Exception):
    pass

class rokoBot:
    def __init__(
            self,
            account: AccountInterface,
            session: ClientSession
            ):
        self.account = account
        self.session = session

    async def logout(self):

        await self.session.close()


    async def login(self):

        try:
            data=await self.account.get_tg_web_data()
            encoded_data = convert_to_url_encoded(data)

            resp = await self.session.post("https://api.roko.love/app/auth",
                                           data=encoded_data,headers=headers,ssl=False)
            resp_json = await resp.json()
            auth_token=resp_json['token']
            self.session.headers['Authorization'] = "Bearer " + auth_token
            return auth_token
        except Exception as err:
            logger.info(f"{err}")
            return False
    async def snake_game(self,name_account):
        data={
	"score": 300
}
        response = await self.session.post('https://api.roko.love/app/tasks/snake-game',json=data,headers=headers,ssl=False)
        rer=await response.json()
        if rer['error'] == False:
            return rer

        else:
            logger.error(
                f"{name_account} | {rer}")
        return rer





    async def check_items(self,name_account):

            response = await self.session.get('https://api.roko.love/app/users/items', headers=headers,
                                               ssl=False)
            rer = await response.json()
            item_ids = [item["item_id"] for item in rer]
            for item in item_ids:
                response = await self.session.post(f'https://api.roko.love/app/items/generators/withdraw/{item}', headers=headers,
                                                  ssl=False)
                rer = await response.json()
                try:
                    if rer['success'] == True:
                        logger.success(
                            f"{name_account} | Box withdraw ROKO +{rer['amount']} ROKO")
                    else:
                        logger.error(
                            f"{name_account} | {rer['message']}")


                except:
                    logger.error(
                        f"{name_account} | {rer}")

            return rer

    async def user_data(self,name_account):
        response = await self.session.get('https://api.roko.love/app/users',headers=headers,ssl=False)
        rer=await response.json()
        return rer
    async def auto_buy_box1(self,name_account):

        response = await self.session.post('https://api.roko.love/app/shop/generator-basic/roko?count=1',headers=headers,ssl=False)
        rer=await response.json()
        try:
            if rer['success'] == True:
                logger.success(
                    f"{name_account} | AutoBuy BOX4000 x1 | -4000ROKO")

        except:
            return rer


        return rer
    async def auto_buy_box2(self,name_account):

        response = await self.session.post('https://api.roko.love/app/shop/generator-minion/roko?count=1',headers=headers,ssl=False)
        rer=await response.json()
        if rer['success'] == True:
            logger.success(
                f"{name_account} | AutoBuy BOX100000 x1 | -100000ROKO")

        return rer


import sys
from .register import logging_info
from loguru import logger

async def logging(text):
    await logging_info()
    logger.warning(text)
def logging_setup():
    format_info = "<green>{time:HH:mm:ss.SS}</green> | <blue>{level}</blue> | <level>{message}</level>"
    logger.remove()

    logger.add(sys.stdout, colorize=True,
               format=format_info, level="INFO")


logging_setup()

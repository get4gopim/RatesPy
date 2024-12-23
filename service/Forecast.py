# REST Client Consumer

import json
import logging
import os
import asyncio
import time

from model import RateInfo, FuelInfo
from collections import namedtuple
from aiohttp import ClientSession, ClientConnectorError, TCPConnector


default_url = 'https://api.saganavis.xyz'
gold_rate_url = '/v1/rates/goldRates'
fuel_rate_url = '/v1/rates/fuelRates'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)

def get_base_aws_uri():
    return default_url

async def fetch(session, url):
    try:
        async with asyncio.wait_for(eternity(), timeout=30.0):
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f'Response Status {response.status} is not OK')
    except asyncio.TimeoutError as ex:
        LOGGER.error(f'Unable to connect remote API : {url} - {repr(ex)}')
        raise ex


async def get_gold_price():
    start = time.time()
    info = None
    url = get_base_aws_uri() + gold_rate_url
    LOGGER.info(url)

    try:
        async with ClientSession() as session:
            html = await fetch(session, url)
            LOGGER.info(f'gold content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = parse_gold_info(html)
            LOGGER.info(f'gold parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Gold API : {repr(ex)}')
        info = RateInfo.RateInfo('0', '0', '0.0', "", "")
        info.set_error(ex)
    except BaseException as ex:
        LOGGER.error(f'Unable to connect Gold API : {repr(ex)}')
        info = RateInfo.RateInfo('0', '0', '0.0', "", "")
        info.set_error(ex)

    LOGGER.info(f'Gold Time Taken {time.time() - start}')
    return info

def parse_gold_info(response):
    print(response)
    x = json.loads(response, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
    info = RateInfo.RateInfo(x.gold22, x.gold24, x.silver, x.date, x.lastUpdated, x.currentDateTime)
    return info

async def get_fuel_price():
    start = time.time()
    info = None
    url = get_base_aws_uri() + fuel_rate_url
    LOGGER.info(url)

    try:
        async with ClientSession() as session:
            html = await fetch(session, url)
            LOGGER.info(f'fuel content fetch in {time.time() - start} secs.')
            parse_start = time.time()
            info = parse_fuel_info(html)
            LOGGER.info(f'fuel parsing took {time.time() - parse_start} secs.')
    except ClientConnectorError as ex:
        LOGGER.error(f'Unable to connect Fuel API : {repr(ex)}')
        info = FuelInfo.FuelInfo('0', '0', "", "")
        info.set_error(ex)
    except BaseException as ex:
        LOGGER.error(f'Unable to connect Fuel API : {repr(ex)}')
        info = FuelInfo.FuelInfo('0', '0', "", "")
        info.set_error(ex)

    LOGGER.info(f'Fuel Time Taken {time.time() - start}')
    return info


def parse_fuel_info(response):
    print(response)
    x = json.loads(response, object_hook=lambda d: namedtuple('x', d.keys())(*d.values()))
    info = FuelInfo.FuelInfo(x.petrol, x.diesel, x.date, x.lastUpdated)
    return info


async def callback(data):
    print(f'inside callback, got: {data}')


def call_apis_async():
    start = time.time()

    gold_data = asyncio.run(get_gold_price())
    asyncio.run(callback(gold_data))

    fuel_data = asyncio.run(get_fuel_price())
    asyncio.run(callback(fuel_data))

    LOGGER.info(f'Total Time Taken {time.time() - start}')
    print()


if __name__ == '__main__':
    LOGGER.info("main started")
    call_apis_async()
    #L = asyncio.gather(get_gold_price(), get_fuel_price())

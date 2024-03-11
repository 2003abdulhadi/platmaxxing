import asyncio
import aiohttp
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=20, period=timedelta(seconds=5).total_seconds())
async def getData(apiUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(apiUrl) as response:
            if response.status == 200:
                return await response.json(content_type='application/json')
            elif response.status == 429:
                await asyncio.sleep(5)
                return await getData(apiUrl)
            else:
                print(response)
                raise Exception()
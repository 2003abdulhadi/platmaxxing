from typing import Any, Dict
from .models import *
import asyncio
import aiohttp

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
            
async def createItem(urlName: str, rank: int=None) -> Item:
    apiUrl = f'https://api.warframe.market/v2/items/{urlName}'

    item: Dict[str, Any] = await getData(apiUrl)
    if not item:
        raise Exception()
    item = item['data']

    if not isinstance(rank, int):
        return Item(item['i18n']['en']['name'],
                    urlName
                    )
    
    return Upgradeable(item['i18n']['en']['name'],
                       urlName,
                       rank
                       )
import asyncio
import json
from pathlib import Path
from ..common import *

async def getSets():
    items = await getData('https://api.warframe.market/v1/items')
    items: Dict[int, Dict[str: str]] = items['payload']['items']
    
    sets = [item for _, item in items.items() if item['item_name'].find('Set') > -1]

    with open('sets.json', 'w') as out:
        json.dump(sets, out)

async def main():
    setsFile = Path('./sets.json')
    if not setsFile.is_file():
        await getSets()

    with open(setsFile) as s:
        sets = json.load(s)
        for set in sets:
            print(set)
    


if __name__ == '__main__':
    asyncio.run(main())
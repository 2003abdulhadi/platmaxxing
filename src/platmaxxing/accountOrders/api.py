import asyncio
from typing import List
from datetime import datetime
from ..common import *

async def getAccountOrders(profileName: str, orderType: OrderType):
    apiUrl = f"https://api.warframe.market/v1/profile/{profileName}/orders"

    orders = await getData(apiUrl)
    orders = orders['payload'][f'{orderType.value}_orders']

    orderObjs: List[Order] = []

    for order in orders:
        rank = order.get('mod_rank', None)

        itemObj = await createItem(order['item']['url_name'], rank)
        orderObj = Order(itemObj,
                         order['quantity'],
                         order['platinum'],
                         datetime.fromisoformat(order['last_update']),
                         order['id'],
                         orderType)

        orderObjs.append(orderObj)

    return orderObjs

async def main():
    profileName = "ParadoxMusic"
    orders = await getAccountOrders(profileName, OrderType['buy'])
    for order in orders:
        print(order)

if __name__ == '__main__':
    asyncio.run(main())
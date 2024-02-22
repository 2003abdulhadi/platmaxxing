import asyncio
from src import *

async def main():
    profileName = "ParadoxMusic"
    orders = await accountOrders.getAccountOrders(profileName, common.OrderType.sell)
    for order in orders:
        print(f'Finding ideal price for {order.item.name}')
        idealPrice = await priceFiltering.getIdealSellingPrice(order.item)
        print(f"The ideal selling price for {order.item.name} is {idealPrice}")

if __name__ == '__main__':
    asyncio.run(main())
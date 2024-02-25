import asyncio
import sys
from typing import Dict
from platmaxxing import *
import pywmapi

async def main():
    email = ''
    password = ''
    
    if len(sys.argv) < 3:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
    else:
        email = sys.argv[1]
        password = sys.argv[2]

    session: pywmapi.auth.Session = None

    try:
        session = pywmapi.auth.signin(email, password)
        print('Logged in Succesfully!')
    except Exception as e:
        print(e)
        print("Failed to login, prices will not be updated")
    
    profileName = "ParadoxMusic"
    print(f'Getting orders for {profileName}')
    orders = await accountOrders.getAccountOrders(profileName, common.OrderType.sell)

    ordersToUpdate: Dict[common.Order, int] = {}

    for order in orders:
        print(f'Finding ideal price for {order.item.name}')
        idealPrice = await priceFiltering.getIdealSellingPrice(order.item)
        print(f"The ideal selling price for {order.item.name} is {idealPrice}")
        ordersToUpdate[order] = idealPrice

        if session:
            if order.price == idealPrice:
                print(f'No need to update {order.item.name}')
                print()
                continue
            print(f'Updating price for {order.item.name}')
            itemRank = order.item.rank if type(order.item) is common.Upgradeable else None
            updatedOrder = pywmapi.orders.update_order(
                session,
                order.id,
                pywmapi.orders.OrderUpdateItem(
                    platinum=idealPrice,
                    quantity=order.quantity,
                    visible=True,
                    rank=itemRank))
            print(f'Updated price for {updatedOrder.item.en.item_name} is {updatedOrder.platinum}')
        print()
            
if __name__ == '__main__':
    asyncio.run(main())
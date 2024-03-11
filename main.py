"""_summary_
"""

import asyncio
import sys
import pywmapi
from platmaxxing import *

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
        print('Logged in Successfully!')
    except Exception as e:
        print(e)
        print("Failed to login, prices will not be updated")
    
    username = ''
    orders = ()
    if session:
        print(f'Getting orders for {session.user.ingame_name}')
        orders = pywmapi.orders.get_current_orders(session)
    else:
        def getAccountOrders():
            global username
            username = input("Enter a username: ")
            try:
                orders = pywmapi.orders.get_orders_by_username(username)
                print(f'Getting orders for {username}')
                return orders
            except:
                print("Invalid username")
                getAccountOrders()

        orders = getAccountOrders()
    username = username if username else session.user.ingame_name
    user = pywmapi.auth.UserShort(None,None,None,None,None,username)

    print('Getting ideal prices')
    idealPrices = await asyncio.gather(
        *[priceFiltering.getIdealSellingPrice(sellOrder) for sellOrder in orders[1]]
    )

    for sellOrder, idealPrice in zip(orders[1], idealPrices):
        sellOrder.user = user

        print(f"The ideal selling price for {sellOrder.item.en.item_name} is {idealPrice}")

        if session:
            if sellOrder.platinum == idealPrice:
                print(f'No need to update {sellOrder.item.en.item_name}')
                print()
                continue
                
            print(f'Updating price for {sellOrder.item.en.item_name}')
            updatedOrder = pywmapi.orders.update_order(
                session,
                sellOrder.id,
                pywmapi.orders.OrderUpdateItem(
                    platinum=idealPrice,
                    quantity=sellOrder.quantity,
                    visible=sellOrder.visible,
                    rank=sellOrder.mod_rank))
            print(f'Updated price for {updatedOrder.item.en.item_name} is {updatedOrder.platinum}')
        print()
            
if __name__ == '__main__':
    asyncio.run(main())
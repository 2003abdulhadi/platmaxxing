import asyncio
import pywmapi
import numpy as np
from math import floor
from platmaxxing.priceFiltering.enums import *
from platmaxxing.common import *

async def getCurrentPrices(item: pywmapi.orders.OrderItem) -> list[int]:

    orders = pywmapi.orders.get_orders(item.item.url_name)

    orders = [order for order in orders if order.order_type.value == 'sell']

    if item.mod_rank is not None:
        orders = [order for order in orders if order.mod_rank == item.mod_rank]

    prices = []

    if any(order.user.status.value == 'ingame' for order in orders):
        prices = [order.platinum for order in orders
                  if order.user.status.value == 'ingame'
                  and (order.user.id != item.user.id if item.user else True)]
    elif any(order.user.status.value == 'online' for order in orders):
        prices = [order.platinum for order in orders
                  if order.user.status.value == 'online'
                  and (order.user.id != item.user.id if item.user else True)]
    else:
        prices = [order.platinum for order in orders
                  if (order.user.id != item.user.id if item.user else True)]

    prices.sort()

    return prices if prices else [0]

async def getHistoricMinimums(item: pywmapi.orders.OrderItem, period: Period=Period.short) -> list[int]:
    apiUrl = f'https://api.warframe.market/v1/items/{item.item.url_name}/statistics'
    
    orders = await getData(apiUrl)
    orders = orders['payload']['statistics_closed'][f'{period.value}']

    if item.mod_rank is not None:
        orders = [order for order in orders if order['mod_rank'] == item.mod_rank]
    
    minimumPrices = [order['min_price'] for order in orders]
    return minimumPrices if minimumPrices else [0]

async def getMedianPrices(item: pywmapi.orders.OrderItem, period: Period=Period.short) -> list[int]:
    apiUrl = f'https://api.warframe.market/v1/items/{item.item.url_name}/statistics'
    
    orders = await getData(apiUrl)
    orders = orders['payload']['statistics_closed'][f'{period.value}']

    if item.mod_rank is not None:
        orders = [order for order in orders if order['mod_rank'] == item.mod_rank]
    
    medianPrices = [order['median'] for order in orders]
    return medianPrices if medianPrices else [0]

async def getIdealSellingPrice(item: pywmapi.orders.OrderItem):
    currentPrices, minimumPrices, medianPrices = await asyncio.gather(
        getCurrentPrices(item),
        getHistoricMinimums(item),
        getMedianPrices(item)
    )

    minimumPrices.sort()
    medianPrices.sort()
    filteredMins = filterOutliers(minimumPrices)
    filteredMedians = filterOutliers(medianPrices)

    minMin = filteredMins[0]
    minMedian = filteredMedians[0]
    currMin = currentPrices[0]

    return floor(max(minMin, minMedian, currMin)) - 1

def filterOutliers(prices):
    if not prices:
        return [-1]

    q1, q3 = np.percentile(prices, [25, 75])
    
    oneHalfIQR = 1.5*(q3 - q1)
    
    lowerBound = q1 - oneHalfIQR
    upperBound = q3 + oneHalfIQR

    filteredPrices = [x for x in prices if lowerBound <= x <= upperBound]
    
    return filteredPrices

# Example usage
async def main():
    item = pywmapi.orders.get_orders_by_username('ParadoxMusic')[1][0]
    idealPrice = await getIdealSellingPrice(item)

    print(f"The ideal selling price for {item.item.en.item_name} is {idealPrice}")

if __name__ == '__main__':
    asyncio.run(main())
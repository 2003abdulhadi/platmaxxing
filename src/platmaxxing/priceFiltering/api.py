from math import floor
import asyncio
import numpy as np
from .enums import *
from ..common import *

async def getCurrentPrices(item: Item):
    apiUrl = f'https://api.warframe.market/v2/orders/item/{item.urlName}'

    orders = await getData(apiUrl)
    orders = orders['data']

    if type(item) is Upgradeable:
        orders = [order for order in orders if order['rank'] == item.rank]
    
    if any(order['user']['status'] == 'ingame' for order in orders):
        prices = [order['platinum'] for order in orders
                if order['type'] == 'sell'
                and order['user']['status'] == 'ingame']
    else:
        prices = [order['platinum'] for order in orders
                if order['type'] == 'sell']
        
    prices.sort()

    return prices

async def getHistoricMinimums(item: Item, period: Period=Period.short):
    apiUrl = f'https://api.warframe.market/v1/items/{item.urlName}/statistics'
    
    orders = await getData(apiUrl)
    orders = orders['payload']['statistics_closed'][f'{period.value}']

    if type(item) is Upgradeable:
        orders = [order for order in orders if order['mod_rank'] == item.rank]
    
    minimumPrices = [order['min_price'] for order in orders]
    return minimumPrices

async def getMedianPrices(item: Item, period: Period=Period.short):
    apiUrl = f'https://api.warframe.market/v1/items/{item.urlName}/statistics'
    
    orders = await getData(apiUrl)
    orders = orders['payload']['statistics_closed'][f'{period.value}']

    if type(item) is Upgradeable:
        orders = [order for order in orders if order['mod_rank'] == item.rank]
    
    medianPrices = [order['median'] for order in orders]
    return medianPrices

async def getIdealSellingPrice(item: Item):
    currentPrices = await getCurrentPrices(item)
    minimumPrices = await getHistoricMinimums(item)
    medianPrices = await getMedianPrices(item)

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
    item = await createItem('saryn_prime_set')
    idealPrice = await getIdealSellingPrice(item.urlName)

    print(f"The ideal selling price for Saryn Prime Set is {idealPrice}")

if __name__ == '__main__':
    asyncio.run(main())
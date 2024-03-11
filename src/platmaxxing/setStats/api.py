import asyncio
import pywmapi
from platmaxxing.common import *
from platmaxxing.priceFiltering import getIdealSellingPrice

async def getSets() -> list[pywmapi.items.ItemShort]:
    """_summary_
    """
    items = pywmapi.items.list_items()

    itemSets = [item for item in items if item.item_name.endswith('Set')]
    
    return itemSets

async def getComponents(itemSet: pywmapi.items.ItemShort) -> list[tuple[pywmapi.orders.OrderItem, int]]:
    apiUrl = f'https://api.warframe.market/v2/items/{itemSet.url_name}/set'
    
    print(f'Getting components for {itemSet.item_name}')

    itemSetData = await getData(apiUrl)
    componentsData = [item for item in itemSetData['data']['items'] if not item['setRoot']]
    components = [(pywmapi.orders.OrderItem(
        id=None,
        platinum=None,
        quantity=None,
        order_type=None,
        platform=None,
        visible=None,
        item=pywmapi.orders.OrderItem.ItemInOrder(
            id=None,
            url_name=component['urlName'],
            icon=None,
            thumb=None,
            tags=[],
            en=pywmapi.orders.OrderItem.ItemInOrder.LangInOrderItem(component['i18n']['en']['name'])
        )
    ),
                   component.get('quantityInSet', 1))
                   for component in componentsData]
    
    print(f'Components for {itemSet.item_name} are {', '.join([f'{component[1]}x {component[0].item.en.item_name}' for component in components])}')

    return components

async def getSetMargins(itemSet: pywmapi.items.ItemShort,
                            components: list[tuple[pywmapi.orders.OrderItem, int]]) -> tuple[pywmapi.items.ItemShort,
                                                                                 int]:
    
    print(f'Getting prices for {itemSet.item_name}')
    
    itemSetAsOrder = pywmapi.orders.OrderItem(
        id=None,
        platinum=None,
        quantity=None,
        order_type=None,
        platform=None,
        visible=None,
        item=pywmapi.orders.OrderItem.ItemInOrder(
            itemSet.id,
            itemSet.url_name,
            None,
            itemSet.thumb,
            [],
            en=pywmapi.orders.OrderItem.ItemInOrder.LangInOrderItem(itemSet.item_name)
        )
    )
    print(f'Getting prices for {itemSet.item_name} set')
    itemSetPrice = await getIdealSellingPrice(itemSetAsOrder)
    print(f'Getting prices for {itemSet.item_name} set components')
    componentPrices = await asyncio.gather(
        *[getIdealSellingPrice(component[0]) for component in components]
    )
    print(f'Calculating sums for {itemSet.item_name}')
    componentPrices = [componentPrice*componentQuantity for componentPrice, componentQuantity in zip(componentPrices, zip(*components)[1])]

    itemComponentsSumPrice = sum(componentPrices)
    margin = itemSetPrice - itemComponentsSumPrice

    print(f'{itemSet.item_name} price is {itemSetPrice}, price for components is {f'{', '.join([f'{f'{componentQuantity}x {component.item.en.item_name} at {componentPrice} ({componentQuantity*componentPrice} total)'}' for (component, componentQuantity), componentPrice in zip(components, componentPrices)])}'}, component sum is {itemComponentsSumPrice} with a margin of {margin} or {round((itemSetPrice/itemComponentsSumPrice), 2)*100}%')
    
    return (itemSet, margin)
    

async def main():
    """_summary_
    """
    itemSets = await getSets()
    
    itemSetComponents = await asyncio.gather(
        *[getComponents(itemSet) for itemSet in itemSets]
    )

    setMargins = await asyncio.gather(
        *[getSetMargins(itemSet, components) for itemSet, components in zip (itemSets, itemSetComponents)],
        return_exceptions=True
    )

    # for itemSet, components in zip(itemSets, itemSetComponents):
    #     await getSetMargins(itemSet, components)

    # for itemSet, margin in setMargins:
    #     print(f'{itemSet.item_name} margin is {margin}')
        
    # for itemSet in itemSets:
    #     print(f'curr: {itemSet.item_name}')
    #     components = await getComponents(itemSet)
    #     setMargin = await getSetMargins(itemSet, components)
    #     setMargins.append(setMargin)

    # setMargins.sort(key=lambda a: a[1])
    # print(f'Sets in order of profitability:')
    # for itemSet, margin in setMargins:
    #     print(f'{itemSet.item_name} has a profit margin of {f'{'+' if margin > 0 else ''}' + margin}')



if __name__ == '__main__':
    asyncio.run(main())


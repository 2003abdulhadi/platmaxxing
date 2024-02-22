from dataclasses import dataclass
from typing import Optional, Final
from datetime import datetime
from .enums import *

@dataclass
class Item:
    name: str
    urlName: str

@dataclass
class Upgradeable(Item):
    rank: int

@dataclass
class Order:
    item: Final[Item]
    quantity: int
    price: int
    lastUpdated: datetime
    id: str
    type: OrderType

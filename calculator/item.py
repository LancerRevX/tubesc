from dataclasses import dataclass

from . import Prices

@dataclass
class Item:
    name: str
    prices: Prices

    def __post_init__(self):
        self.tubes = []
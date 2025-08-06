from dataclasses import dataclass
from abc import ABC, abstractmethod

from . import Prices, Multipliers

@dataclass
class BaseUnit(ABC):
    prices: Prices
    multipliers: Multipliers

    @property
    @abstractmethod
    def price(self) -> float:
        pass
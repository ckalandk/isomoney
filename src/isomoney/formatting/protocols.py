from typing import Protocol
from decimal import Decimal
from isomoney.currency import Currency
from isomoney.rounding import RoundingPolicy
from .formatspec import FormatSpec, Display

__all__ = ["CcyFormatter"]

class _SupportMoneyOperation(Protocol):

    @property
    def currency(self) -> Currency:
        ...

    def to_decimal(self) -> Decimal:
        ...

        
class CcyFormatter(Protocol):
    ctx: FormatSpec

    @property
    def locale(self) -> str:
        ...

    @locale.setter
    def locale(self, value: str) -> None:
        ...

    def configure(
            self, 
            *, 
            compact: bool,
            accounting: bool,
            group_separator: bool,
            ccy_display: Display
            ) -> None:
        ...        


    def format(
              self, 
              amount: Decimal, 
              currency: str, 
              ctx: FormatSpec, 
              *,
              precision: int, 
              rounding: RoundingPolicy, 
              omit_trailing_zeros:bool
            ) -> str:
        ...



                
                
from typing import Protocol
from decimal import Decimal
from .formatspec import FormatSpec

__all__ = ["CcyFormatter"]

class _SupportMoneyOperation(Protocol):

    @property
    def currency(self) -> str:
        ...

    def to_decimal(self) -> Decimal:
        ...

        
class CcyFormatter(Protocol):
    locale: str

    def format(self, amount: Decimal, currency: str, ctx: FormatSpec) -> str:
        ...
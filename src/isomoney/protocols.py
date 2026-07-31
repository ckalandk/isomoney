from typing import Protocol
from isomoney import Currency
from decimal import Decimal
from .formatspec import FormatSpec

__all__ = ["CcyFormatter"]

class _SupportsMoneyFormatting(Protocol):

    @property
    def currency(self) -> Currency:
        ...

    def to_decimal(self) -> Decimal:
        ...

class CcyFormatter(Protocol):
    locale: str
    currency: str

    def format(self, amount: Decimal, ctx: FormatSpec) -> str:
        ...
from typing import Protocol, Literal
from isomoney import Currency
from decimal import Decimal
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class FormatSpec:
    compact: bool
    accounting: bool
    group_separator:bool = True
    ccy_display: Literal["h", "s", "n"] = "s"

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
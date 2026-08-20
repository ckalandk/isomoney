from decimal import Decimal
from typing import Protocol

from pycents.currency import Currency


class _SupportMoneyOperation(Protocol):
    @property
    def currency(self) -> Currency: ...

    def to_decimal(self) -> Decimal: ...

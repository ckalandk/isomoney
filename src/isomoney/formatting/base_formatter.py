from abc import ABC, abstractmethod
from decimal import Decimal

from isomoney.rounding import RoundingMode

from .formatspec import Display, FormatSpec


class CcyFormatter(ABC):
    """Base class for all Money's backend formatter"""

    def __init__(self, locale: str):
        self._locale = locale
        self._default_spec = FormatSpec()

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value

    def configure(
        self,
        *,
        compact: bool = False,
        accounting: bool = False,
        group_separator: bool = True,
        ccy_display: Display = "symbol",
    ) -> None:
        self._default_spec = FormatSpec(
            compact=compact,
            accounting=accounting,
            group_separator=group_separator,
            ccy_display=ccy_display,
        )

    @abstractmethod
    def format(
        self,
        amount: Decimal,
        currency: str,
        ctx: FormatSpec,
        *,
        precision: int,
        rounding: RoundingMode,
        omit_trailing_zeros: bool,
    ) -> str:
        raise NotImplementedError

from abc import ABC, abstractmethod
from decimal import Decimal

from isomoney.rounding import RoundingMode

from .formatspec import DisplayOpts, FormatSpec


class BaseFormatter(ABC):
    """Base class for all Money's backend formatter"""

    def __init__(self, locale: str):
        self._locale = locale
        self._default_spec = FormatSpec()
        self._numbering_system: str | None = None
        self._rounding: RoundingMode = RoundingMode.HALF_EVEN

    @property
    def locale(self) -> str:
        return str(self._locale)

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value

    @property
    def numbering_system(self) -> str | None:
        return self._numbering_system

    @numbering_system.setter
    def numbering_system(self, value: str | None) -> None:
        self._validate_numbering_system(value)
        self._numbering_system = value

    @abstractmethod
    def _validate_numbering_system(self, value: str | None) -> None:
        """
        Backends must implement this to reject invalid numbering systems.

        Raise UnsupportedBackendFeatureError if invalid.
        """
        pass

    def configure(
        self,
        *,
        ccy_display: DisplayOpts = "symbol",
        compact: bool = False,
        compact_precision: int = 1,
        accounting: bool = False,
        group_separator: bool = True,
        rounding: RoundingMode = RoundingMode.HALF_EVEN,
    ) -> None:
        self._default_spec = FormatSpec(
            compact=compact,
            compact_precision=compact_precision,
            accounting=accounting,
            group_separator=group_separator,
            ccy_display=ccy_display,
        )
        self._rounding = rounding

    @abstractmethod
    def format(
        self,
        amount: Decimal,
        currency: str,
        spec: FormatSpec,
    ) -> str:
        raise NotImplementedError

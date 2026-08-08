from __future__ import annotations

import re
from typing import Literal

from isomoney.exceptions import InvalidFormatSpecError
from isomoney.rounding import RoundingMode

from .base_formatter import CcyFormatter
from .formatspec import FormatSpec
from .protocols import _SupportMoneyOperation
from .std_formatter import StdFormatter

type _CurrencyDisplay = Literal[
    "hidden",
    "symbol",
    "iso",
    "name",
]

_map_symbol: dict[str, _CurrencyDisplay] = {"h": "hidden", "i": "iso", "n": "name"}


class MoneyFormat:
    # TODO: !r and !s format field must be handled
    _FORMAT_SPEC_PATTERN = re.compile(
        r"^(?P<display>[hin])?(?P<compact>c)?(?P<accounting>a)?(?P<group_sep>u)?(?P<rest>.*)$"
    )

    def __init__(
        self,
        *,
        precision: int | None = None,
        rounding: RoundingMode = RoundingMode.HALF_UP,
        omit_trailing_zeros: bool = True,
        formatter: CcyFormatter | None = None,
    ) -> None:
        self.precision = precision
        self.rounding = rounding
        self.omit_trailing_zeros = omit_trailing_zeros
        self.backend_formatter = formatter if formatter else StdFormatter()

    def _parse(self, fmt_spec: str) -> tuple[FormatSpec | None, str]:
        match = self._FORMAT_SPEC_PATTERN.fullmatch(fmt_spec)
        if match is None:
            raise InvalidFormatSpecError(
                f"Invalid format specifier '{fmt_spec}' for object of type 'Money'"
            )

        if all(
            match[key] is None
            for key in ["display", "compact", "group_sep", "accounting"]
        ):
            return None, match["rest"]

        return FormatSpec(
            compact=match["compact"] is not None,
            accounting=match["accounting"] is not None,
            ccy_display=(
                self.backend_formatter._default_spec.ccy_display
                if match["display"] is None
                else _map_symbol[match["display"]]
            ),
            group_separator=match["group_sep"] is None,
        ), match["rest"]

    def format(self, money: _SupportMoneyOperation, format_spec: str) -> str:
        context, rest = self._parse(format_spec)
        if context is None:
            str_money = self.backend_formatter.format(
                money.to_decimal(),
                money.currency.ccy_code,
                self.backend_formatter._default_spec,
                precision=(
                    self.precision
                    if self.precision is not None
                    else money.currency.minor_units
                ),
                rounding=self.rounding,
                omit_trailing_zeros=self.omit_trailing_zeros,
            )
            return format(str_money, rest)
        precision = (
            self.precision if self.precision is not None else money.currency.minor_units
        )
        str_money = self.backend_formatter.format(
            money.to_decimal(),
            money.currency.ccy_code,
            context,
            precision=precision,
            rounding=self.rounding,
            omit_trailing_zeros=self.omit_trailing_zeros,
        )
        return format(str_money, rest)

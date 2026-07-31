from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import Protocol, Callable, Literal
from dataclasses import dataclass
import re
from .currency import Currency
from isomoney.formatters import _SupportsMoneyFormatting, FormatSpec, CcyFormatter, BabelFormatter

class MoneyFormat:

    _FORMAT_SPEC_PATTERN = re.compile(
       r"^(?P<display>[hin])?(?P<compact>c)?(?P<accounting>a)?(?P<separator>g)?(?P<rest>.*)$"
    )

    def __init__(self, 
                 *, 
                 precision: int = 2, 
                 rounding: str = ROUND_HALF_UP,
                 omit_trailing_zeros = True,
                 ccy_format: CcyFormatter | None = None
                 ):
        self.precision = precision
        self.rounding = rounding
        self.omit_trailing_zeros = omit_trailing_zeros
        self.ccy_format = ccy_format if ccy_format else BabelFormatter('USD', 'en_US')

    def _parse(self, fmt_spec: str):
        match = self._FORMAT_SPEC_PATTERN.fullmatch(fmt_spec)
        if match is None:
            raise ValueError(
                f"Invalid format specifier '{fmt_spec}' for object of type 'Money'"
            )
        return FormatSpec(
                compact=match["compact"] is not None,
                accounting=match["accounting"] is not None,
                ccy_display=(
                    match["display"]
                    if match["display"] else ""),
                ), match["rest"]

    def format(self, money: _SupportsMoneyFormatting, format_spec: str) -> str:
        context, rest = self._parse(format_spec)
        arg = self.ccy_format.format(money.to_decimal(), self.ccy_format.currency, context)

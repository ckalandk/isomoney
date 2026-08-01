from __future__ import annotations
from decimal import Decimal
import re
from .protocols import CcyFormatter, _SupportMoneyOperation
from .formatspec import FormatSpec
from .std_formatter import StdFormatter
from isomoney.rounding import RoundingPolicy

_map_symbol = {
    "h": "hidden",
    "i": "iso",
    "n": "name"
}
class MoneyFormat:

    _FORMAT_SPEC_PATTERN = re.compile(
       r"^(?P<display>[hin])?(?P<compact>c)?(?P<group_sep>u)?(?P<accounting>a)?(?P<rest>.*)$"
    )

    def __init__(self,
                 *, 
                 precision: int = 2, 
                 rounding: RoundingPolicy = RoundingPolicy.HALF_UP,
                 omit_trailing_zeros = True,
                 formatter: CcyFormatter | None = None
                 ):
        self.precision = precision
        self.rounding = rounding
        self.omit_trailing_zeros = omit_trailing_zeros
        self.ccy_format = formatter if formatter else StdFormatter()

    def _parse(self, fmt_spec: str) -> tuple[FormatSpec, str]:
        match = self._FORMAT_SPEC_PATTERN.fullmatch(fmt_spec)
        if match is None:
            raise ValueError(
                f"Invalid format specifier '{fmt_spec}' for object of type 'Money'"
            )
        return FormatSpec(
                compact=match["compact"] is not None,
                accounting=match["accounting"] is not None,
                ccy_display=(
                    _map_symbol.get(match["display"], "symbol")
                ),
                group_separator=match["group_sep"] is None
                ), match["rest"]

    def format(self, money: _SupportMoneyOperation, format_spec: str) -> str:
        context, rest = self._parse(format_spec)
        arg = self.ccy_format.format(money.to_decimal(), money.currency.ccy_code, context)
        return format(arg, rest)

from .protocols import CcyFormatter
from isomoney.rounding import RoundingPolicy, as_decimal_rounding
from isomoney.exceptions import InvalidFormatSpecError
from isomoney.currency import Ccy
from .formatspec import FormatSpec, Display, _is_display
from decimal import Decimal
from isomoney._decimal import _decimal_places


__all__ = ["StdFormatter"]


def _format_compact_decimal(number: Decimal) -> tuple[Decimal, str]:
    """
    Format a number in compact form (e.g., 1,000 -> 1K, 1,000,000 -> 1M).
    """

    abs_number = abs(number)
    if abs_number >= 1_000_000_000:
        return number / Decimal(1_000_000_000), "B"
    elif abs_number >= 1_000_000:
        return number / Decimal(1_000_000), "M"
    elif abs_number >= 1_000:
        return number / Decimal(1_000), "K"
    else:
        return number, ""


def _get_currency_symbol(currency: str, display_option: str) -> str:
    _map_display = {
        "iso": Ccy[currency].ccy_code,
        "name": Ccy[currency].ccy_name,
        "hidden": ""
    }
    try:
        symbol = _map_display[display_option]
        return symbol
    except KeyError:
        raise AssertionError(
            f"Invalid currency display option: {display_option}. "
        ) from None

    
class StdFormatter(CcyFormatter):
    def __init__(self, locale: str | None = None) -> None:
        self.locale = locale if locale else ""
        self.ctx = FormatSpec(
            compact=False,
            accounting=False,
            group_separator=True,
            ccy_display="iso"
        )

    def configure(
            self, 
            *, 
            compact: bool,
            accounting: bool,
            group_separator: bool,
            ccy_display: Display
        ) -> None:
        self.ctx = FormatSpec(
            compact=compact,
            accounting=accounting,
            group_separator=group_separator,
            ccy_display=ccy_display
        )
    def format(
        self, 
        amount: Decimal,
        currency:str, 
        ctx: FormatSpec, 
        *,
        precision:int, 
        rounding: RoundingPolicy, 
        omit_trailing_zeros:bool
    ) -> str:
        rnd_plcy = as_decimal_rounding(rounding)
        if ctx.ccy_display == "symbol":
            raise InvalidFormatSpecError(
                f"{type(self).__name__} doesn't support symbol currency display." 
                 "Use IcuFormatter or BabelFormatter instead."
            )
        symbol = _get_currency_symbol(currency, ctx.ccy_display)
        suffix = ""
        if ctx.compact:
            amount, suffix = _format_compact_decimal(amount)
            amount = amount.quantize(Decimal(f"1.{'0'*precision}"), rounding=rnd_plcy)
            if omit_trailing_zeros and _decimal_places(amount) > 0:
                amount = amount.normalize()

        if ctx.group_separator:
            number = format(amount, ",")
        else:
            number = format(amount, "f")

        if ctx.accounting and amount < 0:
            number = number.lstrip("-")
            symbol = f" {symbol}" if symbol else ""
            str_amount = f"({number}{suffix}{symbol})"
        else:
            str_amount = f"{number}{suffix} {symbol}"

        return str_amount.strip()
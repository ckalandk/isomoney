from .protocols import CcyFormatter, FormatSpec
from decimal import Decimal
from babel.numbers import (
    format_decimal, 
    format_compact_decimal, 
    format_currency, 
    format_compact_currency
)
from functools import partial   
from isomoney import InvalidFormatSpecError
    
_babel_format_currency = (
    partial(format_currency, 
            currency_digits=False, 
            format=None, 
            decimal_quantization=False
    )
)

 
class BabelFormatter(CcyFormatter):
    def __init__(self, currency: str, locale: str) -> None:
        self.currency = currency
        self.locale = locale

    def format(self, amount: Decimal, ctx: FormatSpec) -> str:
        if ctx.accounting and (ctx.compact or ctx.ccy_display in {"n", "h"}):
            raise InvalidFormatSpecError(
                f"Format specification not supported by {type(self).__name__}"
            )
        if ctx.compact and ctx.ccy_display == "n":
            raise InvalidFormatSpecError(
                f"Format specification not supported by {type(self).__name__}"
            )
                
        if ctx.ccy_display == "h":
            if not ctx.compact:
                return format_decimal(
                    amount, locale=self.locale, decimal_quantization=False
                )
            else:
                return format_compact_decimal(amount, locale=self.locale)
        if ctx.compact:
            return format_compact_currency(
                amount, 
                self.currency, 
                locale=self.locale, 
            )
        if ctx.ccy_display == "n":
            fmt_type = "name"
        else:
            fmt_type = "accounting" if ctx.accounting else "standard"
        return _babel_format_currency(
            amount, 
            self.currency, 
            locale=self.locale, 
            format_type=fmt_type
        )
        


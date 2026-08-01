from .protocols import CcyFormatter
from isomoney.rounding import RoundingPolicy
from .formatspec import FormatSpec

import decimal

class StdFormatter(CcyFormatter):
    def __init__(self, locale: str|None = None) -> None:
        self.locale = locale

    def format(
        self, 
        amount: decimal.Decimal,
        currency:str, 
        ctx: FormatSpec, 
        precision:int = 2, 
        rounding: str = RoundingPolicy.HALF_EVEN, 
        omit_trailing_zeros:bool = False
    ) -> str:
        return f"{amount!r} ------------- it worked {self.locale!s}"

        
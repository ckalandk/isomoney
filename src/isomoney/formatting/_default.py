from .format import MoneyFormat
from .std_formatter import StdFormatter
from .protocols import _SupportMoneyOperation
from isomoney.rounding import RoundingPolicy
    
_default = MoneyFormat(
    formatter=StdFormatter()
)

def format(money: _SupportMoneyOperation, format_spec: str):
    return _default.format(money, format_spec)

def basicConfig(*, 
        precision:int, 
        rounding: RoundingPolicy,
        omit_trailing_zeros:bool) -> None:
    
    _default.precision = precision
    _default.rounding = rounding
    _default.omit_trailing_zeros = omit_trailing_zeros
    
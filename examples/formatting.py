from decimal import Decimal

from isomoney.formatting.formatspec import FormatSpec
from isomoney.formatting.std_formatter import StdFormatter

std_formatter = StdFormatter()
ctx = FormatSpec(compact=True, ccy_display="iso")
result = std_formatter.format(
    Decimal("12.00"), "USD", ctx, precision=2, omit_trailing_zeros=True
)
print(result)

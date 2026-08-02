from decimal import Decimal

from isomoney import Ccy, Money
from isomoney.formatting import MoneyFormat
from isomoney.formatting.formatspec import FormatSpec
from isomoney.formatting.std_formatter import StdFormatter

fmt = MoneyFormat(formatter=StdFormatter())
ctx = FormatSpec(
    compact=False, accounting=False, ccy_display="iso", group_separator=True
)
mny = Money.from_major(Decimal("-1234567.89"), Ccy.USD)

print(fmt.format(mny, "iu"))  # Output: 1,234,567.89 USD

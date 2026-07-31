from decimal import Decimal
from isomoney import Ccy, Money

from isomoney.formatting import IcuFormatter
from isomoney.rounding import RoundingPolicy
from isomoney.formatspec import FormatSpec

policy = RoundingPolicy.DOWN

fmt = IcuFormatter("EUR", "en_US")

ctx = FormatSpec(compact=True, accounting=False,
                 group_separator=True, ccy_display="symbol")
result = fmt.format(Decimal("-2940050299"), ctx, omit_trailing_zeros=True, precision=2, rounding=policy)
print(result)

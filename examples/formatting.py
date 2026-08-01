from decimal import Decimal
from isomoney import Ccy, Money

from isomoney.formatting import IcuFormatter, FormatSpec
from isomoney.rounding import RoundingPolicy


policy = RoundingPolicy.DOWN

fmt = IcuFormatter("en_US")

ctx = FormatSpec(compact=True, accounting=False,
                 group_separator=True, ccy_display="symbol")
result = fmt.format(Decimal("-2940050299"), currency="USD", ctx=ctx, omit_trailing_zeros=True, precision=2, rounding=policy)
print(result)

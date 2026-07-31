from decimal import Decimal
from isomoney import Ccy, Money

from isomoney.formatters import BabelFormatter, FormatSpec

fmt = BabelFormatter("USD", "en_US")
ctx = FormatSpec(compact=False, accounting=False, group_separator=True, ccy_display="n")
result = fmt.format(Decimal("2950050.299"), ctx)
print(result)
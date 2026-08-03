from decimal import Decimal

from isomoney import Ccy, Money, formatting

formatting.basicConfig(precision=2, omit_trailing_zeros=False)

mny = Money.from_major(Decimal("-12345670000000"), Ccy.USD)

print(f"{mny!r:>80}")

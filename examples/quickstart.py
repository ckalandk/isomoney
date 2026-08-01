from decimal import Decimal

from isomoney import Ccy, Money

# Constructing money amounts.
price = Money.from_major(Decimal("29.99"), "USD")
bonus = Money.from_major(5.00, Ccy.USD)
tax = Money.from_major(Decimal("2.00"), "USD")

# Arithmetic operations.
total = price + bonus - tax

# Comparisons.
assert price < total
assert price != total

# Accessing the internal representation (minor units).
print(total.minor_units)

# Converting back to major units.
print(total.to_decimal())

# Currency information.
print(total.currency.ccy_code)
print(total.currency.minor_units)
print("Currency name:", total.currency.ccy_name)

# String representations.
print(total)
print(repr(total))
print(f"{total:h}")
from decimal import Decimal

from isomoney import Money
from isomoney.money import Unrounded

chair = Money.from_major(101, "JPY")
desk = Money.from_major(104, "JPY")

tax = Decimal("1.10")

chair_taxed = chair * tax  # ¥111.10
desk_taxed = desk * tax  # ¥114.40

unrounded_total = chair_taxed + desk_taxed  # ¥225.50
print(unrounded_total.quantize())  # 226
total_amount2 = chair_taxed.quantize() + desk_taxed.quantize()
print(total_amount2)

print("-----------------------------------------------")
result = chair + desk
assert type(result) is Money

result = chair + desk * 1.15
assert type(result) is Unrounded

result = chair * 2
assert type(result) is Money

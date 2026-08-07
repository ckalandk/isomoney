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

unit_price = Money.from_major(12.99, "USD")
number_of_items = 15
total_price = unit_price * number_of_items
assert type(total_price) is Money

salary = Money.from_major(1500.45, "USD")
bonified_salary = (salary * 1.3).quantize()

print(bonified_salary)

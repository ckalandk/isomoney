from isomoney._decimal import _decimal_places, _remove_trailing_zeros
from decimal import Decimal
import pytest

@pytest.mark.parametrize(
    "value, precision, expected",
    [
        (Decimal('2.56'), 2, Decimal('2.56')),
        (Decimal('2.56'), 3, Decimal('2.560')),
        (Decimal('2.00'), 0, Decimal('2')),
        (Decimal('2.00'), 1, Decimal('2.0')),
        (Decimal('2.00'), 2, Decimal('2.00')),
        (Decimal('22500'), 0, Decimal('22500')),
        (Decimal('22500'), 2, Decimal('22500.00')),
    ],
)
def test_decimal_remove_trailing_zeros(value, precision, expected):
    assert _remove_trailing_zeros(value, precision) == expected
from decimal import Decimal

import pytest

from isomoney._decimal import _remove_trailing_zeros


@pytest.mark.parametrize(
    "value, expected",
    [
        (Decimal("2.56"), -2),
        (Decimal("2.00"), 0),
        (Decimal("2.00"), 0),
        (Decimal("22500"), 0),
    ],
)
def test_decimal_remove_trailing_zeros(value, expected):
    assert _remove_trailing_zeros(value).as_tuple().exponent == expected

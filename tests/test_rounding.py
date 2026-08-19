import decimal

import pytest

from isomoney.rounding import RoundingMode, as_decimal_rounding


@pytest.mark.parametrize(
    "policy, expected",
    [
        (RoundingMode.CEILING, decimal.ROUND_CEILING),
        (RoundingMode.FLOOR, decimal.ROUND_FLOOR),
        (RoundingMode.DOWN, decimal.ROUND_DOWN),
        (RoundingMode.UP, decimal.ROUND_UP),
        (RoundingMode.HALF_EVEN, decimal.ROUND_HALF_EVEN),
        (RoundingMode.HALF_DOWN, decimal.ROUND_HALF_DOWN),
        (RoundingMode.HALF_UP, decimal.ROUND_HALF_UP),
    ],
)
def test_to_decimal(policy, expected):
    assert as_decimal_rounding(policy) == expected


@pytest.mark.parametrize(
    "policy",
    [
        RoundingMode.HALF_ODD,
        RoundingMode.HALF_CEILING,
        RoundingMode.HALF_FLOOR,
        RoundingMode.UNNECESSARY,
    ],
)
def test_to_decimal_unsupported(policy):
    with pytest.raises(NotImplementedError):
        as_decimal_rounding(policy)

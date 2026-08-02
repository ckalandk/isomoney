import decimal
import pytest

from isomoney.rounding import RoundingPolicy, as_decimal_rounding


@pytest.mark.parametrize(
    "policy, expected",
    [
        (RoundingPolicy.CEILING, decimal.ROUND_CEILING),
        (RoundingPolicy.FLOOR, decimal.ROUND_FLOOR),
        (RoundingPolicy.DOWN, decimal.ROUND_DOWN),
        (RoundingPolicy.UP, decimal.ROUND_UP),
        (RoundingPolicy.HALF_EVEN, decimal.ROUND_HALF_EVEN),
        (RoundingPolicy.HALF_DOWN, decimal.ROUND_HALF_DOWN),
        (RoundingPolicy.HALF_UP, decimal.ROUND_HALF_UP),
    ],
)
def test_to_decimal(policy, expected):
    assert as_decimal_rounding(policy) == expected


@pytest.mark.parametrize(
    "policy",
    [
        RoundingPolicy.HALF_ODD,
        RoundingPolicy.HALF_CEILING,
        RoundingPolicy.HALF_FLOOR,
        RoundingPolicy.UNNECESSARY,
    ],
)
def test_to_decimal_unsupported(policy):
    with pytest.raises(NotImplementedError):
        as_decimal_rounding(policy)
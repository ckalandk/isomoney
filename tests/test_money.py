from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from isomoney import Ccy, Currency, Money
from isomoney.exceptions import CurrencyMismatchError
from isomoney.rounding import RoundingPolicy


@pytest.fixture
def money():
    def _amount(amount=200, ccy="USD"):
        return Money(amount, currency=Currency.of(ccy))

    return _amount


@pytest.fixture
def usd():
    return Currency(Ccy.USD)


@st.composite
def ordered_pairs(draw):
    n1 = draw(st.integers())
    n2 = draw(st.integers(min_value=n1))
    return (n1, n2)


@st.composite
def strict_ordered_pairs(draw):
    n1 = draw(st.integers())
    n2 = draw(st.integers(min_value=n1 + 1))
    return (n1, n2)


@st.composite
def ccy_code(draw):
    return draw(st.from_type(Ccy))


@pytest.mark.parametrize(
    "minor_units, currency",
    [
        pytest.param(100, Currency(Ccy.USD), id="usd"),
        pytest.param(123456000, Currency(Ccy.EUR), id="eur"),
        pytest.param(-100, Currency(Ccy.JPY), id="negative amount"),
    ],
)
def test_money_init(minor_units, currency):
    money = Money(minor_units, currency=currency)

    assert money.minor_units == minor_units
    assert money.currency == currency


def test_money_instances_are_immutable(money):
    with pytest.raises(AttributeError, match="Money instances are immutable"):
        money()._amount = 1000


@pytest.mark.parametrize(
    "amount,currency,expected",
    [
        pytest.param(
            Decimal("29"),
            "USD",
            2900,
            id="USD whole dollars",
        ),
        pytest.param(
            Decimal("29.3400"),
            "USD",
            2934,
            id="USD two decimals",
        ),
        pytest.param(
            Decimal("29000"),
            "JPY",
            29000,
            id="JPY no minor units",
        ),
        pytest.param(
            Decimal("29.123"),
            "KWD",
            29123,
            id="KWD three decimal places",
        ),
    ],
)
def test_from_major(amount, currency, expected):
    money = Money.from_major(amount, currency)
    assert money.minor_units == expected


@pytest.mark.parametrize(
    "amount,currency,expected",
    [
        pytest.param(
            Decimal("29.345"),
            "USD",
            Decimal("29.35"),
            id="USD too many fractional digits",
        ),
        pytest.param(
            Decimal("29.1"),
            "JPY",
            Decimal("30"),
            id="JPY fractional amount",
        ),
        pytest.param(
            Decimal("29.1234"),
            "KWD",
            Decimal("29.124"),
            id="KWD four fractional digits",
        ),
    ],
)
def test_from_major_rejects_numbers_with_more_then_minor_unit_decimals(
    amount, currency, expected
):
    mny = Money.from_major(amount, currency, rounding=RoundingPolicy.UP)
    assert mny.to_decimal() == expected


@pytest.mark.parametrize(
    "svalue",
    [
        pytest.param(
            Decimal("Inf"),
            id="positive Infinity",
        ),
        pytest.param(
            Decimal("-Inf"),
            id="negative Infinity",
        ),
        pytest.param(
            Decimal("NaN"),
            id="Quiet NaN",
        ),
        pytest.param(
            Decimal("sNaN"),
            id="Signaling NaN",
        ),
    ],
)
def test_from_major_rejects_non_finite_decimals(svalue):
    with pytest.raises(ValueError) as exc_info:
        Money.from_major(svalue, "USD")
    assert str(exc_info.value) == f"Special/infinite values are forbidden: {svalue!s}"


# Testing the Comparisons
@pytest.mark.parametrize(
    "self_,other,expected",
    [
        pytest.param(
            Money(199, currency=Currency(Ccy.USD)),
            Money(199, currency=Currency(Ccy.USD)),
            True,
            id="Same amount, same currencies",
        ),
        pytest.param(
            Money(199, currency=Currency(Ccy.USD)),
            Money(199, currency=Currency(Ccy.EUR)),
            False,
            id="Same amounts, different currencies",
        ),
        pytest.param(
            Money(199, currency=Currency(Ccy.USD)),
            Money(200, currency=Currency(Ccy.USD)),
            False,
            id="Different amounts, same currencies",
        ),
        pytest.param(
            Money(199, currency=Currency(Ccy.USD)),
            Money(200, currency=Currency(Ccy.EUR)),
            False,
            id="Different amounts, Different currencies",
        ),
        pytest.param(
            Money(199, currency=Currency(Ccy.USD)),
            object(),
            False,
            id="Comparing with object",
        ),
    ],
)
def test_money_equality(self_, other, expected):
    assert (self_ == other) == expected


@given(strict_ordered_pairs())
def test_money_strict_comparison(pair):
    n1, n2 = pair
    ccy = Currency(Ccy.USD)
    left, right = Money(n1, currency=ccy), Money(n2, currency=ccy)
    assert left < right
    assert right > left


@given(ordered_pairs())
def test_money_equality_comparison(pair):
    n1, n2 = pair
    ccy = Currency(Ccy.USD)
    left, right = Money(n1, currency=ccy), Money(n2, currency=ccy)
    assert left <= right
    assert right >= left


def test_money_comparison_not_implemented_for_non_money(money):
    assert money().__lt__(object()) is NotImplemented


def test_money_comparison_raises_when_operands_have_different_currencies(money):
    other = money(499, "EUR")
    with pytest.raises(
        CurrencyMismatchError,
        match="Cannot compare money values with different currencies",
    ):
        _ = money() < other


# Test Arithmetic operations
@given(n=st.integers(), m=st.integers())
def test_money_add_return_the_right_amount(n, m):
    left = Money(n, currency=Currency(Ccy.USD))
    right = Money(m, currency=Currency(Ccy.USD))
    result = left + right
    assert result.minor_units == n + m


@given(
    left=st.integers(),
    right=st.integers(),
)
def test_money_add_is_commutative(left, right):
    ccy = Currency(Ccy.USD)

    left = Money(left, currency=ccy)
    right = Money(right, currency=ccy)
    assert left + right == right + left


@given(
    first=st.integers(),
    second=st.integers(),
    third=st.integers(),
)
def test_money_add_is_associative(first, second, third):
    first = Money(first, currency=Currency(Ccy.USD))
    second = Money(second, currency=Currency(Ccy.USD))
    third = Money(third, currency=Currency(Ccy.USD))

    assert first + (second + third) == (first + second) + third


def test_money_add_not_implemented_for_non_money(money):
    assert money().__add__(object()) is NotImplemented


def test_money_add_raises_when_operand_have_different_currencies(money):
    left = money(100, "USD")
    right = money(200, "EUR")
    with pytest.raises(
        CurrencyMismatchError,
        match="Cannot add money amounts with different currencies.",
    ):
        _ = left + right


@given(st.integers(), st.integers())
def test_money_sub_return_the_right_amount(n, m):
    left = Money(n, currency=Currency(Ccy.USD))
    right = Money(m, currency=Currency(Ccy.USD))
    result = left - right
    assert result.minor_units == n - m


@given(st.integers())
def test_money_sub_is_zero_when_operands_are_equal(n):
    left = Money(n, currency=Currency(Ccy.USD))
    right = Money(n, currency=Currency(Ccy.USD))
    result = left - right
    assert result.minor_units == 0


def test_money_sub_not_implemented_for_non_money(money):
    assert money().__sub__(object()) is NotImplemented


@given(st.integers())
def test_money_negation(n):
    money = Money(n, currency=Currency(Ccy.USD))

    assert (-money).minor_units == -n


@given(st.integers())
def test_money_negation_is_additive_inverse(n):
    money = Money(n, currency=Currency(Ccy.USD))
    zero = Money(0, currency=Currency(Ccy.USD))

    assert money + (-money) == zero


@given(st.integers(), st.integers())
def test_money_add_and_sub_are_compatible(n, m):
    left = Money(n, currency=Currency(Ccy.USD))
    right = Money(m, currency=Currency(Ccy.USD))
    result = Money(n - m, currency=Currency(Ccy.USD))
    assert right + result == left


@pytest.mark.parametrize(
    "money_,expected",
    [
        pytest.param(
            Money(1234, currency=Currency(Ccy.USD)),
            Decimal("12.34"),
            id="Currency with two minor_unit",
        ),
        pytest.param(
            Money(1234, currency=Currency(Ccy.JPY)),
            Decimal("1234"),
            id="Currency with 0 minor_unit",
        ),
        pytest.param(
            Money(1234, currency=Currency(Ccy.KWD)),
            Decimal("1.234"),
            id="Currency with 3 minor_unit",
        ),
        pytest.param(
            Money(12000, currency=Currency(Ccy.KWD)),
            Decimal("12.000"),
            id="Add minor_unit trailing zeros",
        ),
    ],
)
def test_money_to_decimal(money_, expected):
    assert money_.to_decimal() == expected


@given(amount=st.integers(), ccy=ccy_code())
def test_money_repr(amount, ccy):
    mny = Money(amount, currency=Currency(ccy))
    assert repr(mny) == f"Money(amount={mny.to_decimal()}, currency='{ccy.ccy_code}')"


@given(amount=st.integers(), ccy=ccy_code())
def test_money_str(amount, ccy):
    mny = Money(999, currency=Currency(ccy))
    assert str(mny) == f"{mny.to_decimal()!s} {ccy.ccy_code}"

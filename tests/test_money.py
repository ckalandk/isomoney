from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from isomoney import Ccy, Currency, Money
from isomoney.exceptions import CurrencyMismatchError
from isomoney.money import AllocationResult
from isomoney.rounding import RoundingPolicy

# TODO add two methods as_dict, from_dict
# use this format for dict {"amount", "2.99", "currency", "USD"}
# from_dict should call from_major


def _usd_money(amount: int, currency: str = "USD") -> Money:
    return Money(amount, Currency.of(currency))


@pytest.fixture(scope="session")
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


@st.composite
def rounding(draw):
    return draw(
        st.from_type(RoundingPolicy).filter(
            lambda rounding: rounding != RoundingPolicy.UNNECESSARY
        )
    )


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


def test_money_with_zero_amounts_are_cached():
    zero1 = Money(0, Currency(Ccy.USD))
    zero2 = Money.from_major(0.0, "USD")
    zero3 = Money.from_major(Decimal("0"), "USD")
    zero4 = Money.zero("USD")

    assert zero1 is zero2
    assert zero2 is zero3
    assert zero1 is zero4


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
def test_from_major_round_numbers_with_more_then_minor_unit_decimals(
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


# Testing Allocation


@given(
    amount=st.integers(0, 1_000_000),
    ratios=st.lists(st.integers(1, 10), min_size=1),
    code=ccy_code(),
)
def test_money_allocation_properties(ratios, amount, code):
    mny = Money(amount, Currency.of(code.ccy_code))
    result = mny.allocate(ratios)

    # Sanity checks
    assert all(isinstance(share, Money) for share in result.shares)
    ccy = result.shares[0].currency
    assert all(result.shares[i].currency == ccy for i in range(1, len(result.shares)))

    # All shares must be positive
    assert all(share >= Money.zero(code.ccy_code) for share in result.shares)

    # Number of shares == Number of ratios
    if ratios:
        assert len(ratios) == len(result.shares)
    else:
        assert len(result.shares) == 1 and result.shares[0] is mny

    # No penny is lost, sum of shares + the remainded must equal the original money
    assert sum(result.shares, Money.zero(code.ccy_code)) + result.remainder == mny


@pytest.mark.parametrize(
    "amount,ratios,expected",
    [
        pytest.param(
            100,
            [1, 1, 1],
            AllocationResult(
                shares=(
                    _usd_money(33),
                    _usd_money(33),
                    _usd_money(33),
                ),
                remainder=_usd_money(1),
            ),
        ),
        pytest.param(
            201,
            [1, 4],
            AllocationResult(
                shares=(_usd_money(40), _usd_money(160)),
                remainder=Money(1, Currency.of("USD")),
            ),
        ),
        pytest.param(
            201,
            [0, 4],
            AllocationResult(
                shares=(_usd_money(0), _usd_money(201)),
                remainder=_usd_money(0),
            ),
        ),
        pytest.param(
            201,
            [],
            AllocationResult(shares=tuple(), remainder=_usd_money(201)),
        ),
    ],
)
def test_money_allocation_examples(amount, ratios, expected):
    mny = Money(amount, Currency.of("USD"))
    result = mny.allocate(ratios)
    assert result == expected


def test_money_allocation_rejects_ratios_with_negative_content(money):
    mny = money("USD")
    with pytest.raises(ValueError, match="ratios cannot contain negative values"):
        mny.allocate([1, 0, -2])


# Testing the Comparisons
@pytest.mark.parametrize(
    "self_,other,expected",
    [
        pytest.param(
            _usd_money(199),
            _usd_money(199),
            True,
            id="Same amount, same currencies",
        ),
        pytest.param(
            _usd_money(199),
            _usd_money(199, "EUR"),
            False,
            id="Same amounts, different currencies",
        ),
        pytest.param(
            _usd_money(199),
            _usd_money(200),
            False,
            id="Different amounts, same currencies",
        ),
        pytest.param(
            _usd_money(199),
            _usd_money(200, "EUR"),
            False,
            id="Different amounts, Different currencies",
        ),
        pytest.param(
            _usd_money(199),
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
def test_money_add_return_expected_amount(n, m):
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
def test_money_sub_return_expected_amount(n, m):
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
            _usd_money(1234),
            Decimal("12.34"),
            id="Currency with two minor_unit",
        ),
        pytest.param(
            _usd_money(1234, "JPY"),
            Decimal("1234"),
            id="Currency with 0 minor_unit",
        ),
        pytest.param(
            _usd_money(1234, "KWD"),
            Decimal("1.234"),
            id="Currency with 3 minor_unit",
        ),
        pytest.param(
            _usd_money(12099, "KWD"),
            Decimal("12.099"),
            id="Add minor_unit trailing zeros",
        ),
    ],
)
def test_money_to_decimal(money_, expected):
    assert money_.to_decimal() == expected


@pytest.mark.parametrize("amount, currency", [(299, "USD"), (199, "KWD"), (220, "EUR")])
def test_money_repr(amount, currency):
    mny = Money(amount, Currency.of(currency))
    assert repr(mny) == f"Money(amount={mny.to_decimal()}, currency='{currency}')"


@pytest.mark.parametrize(
    "amount, currency",
    [(299, "USD"), (199, "KWD"), (220, "EUR")],
)
def test_money_str(amount, currency):
    mny = Money(amount, Currency.of(currency))
    assert str(mny) == f"{mny.to_decimal()!s} {currency}"


@st.composite
def _any_money_unrounded(draw) -> Money._Unrounded:
    amount = draw(st.integers(min_value=-(10**19), max_value=10**19))
    return Money._Unrounded(Money(amount, Currency.of("USD")))


decimals = st.decimals(
    min_value=Decimal("0"),
    max_value=Decimal("100"),
    places=6,
    allow_nan=False,
    allow_infinity=False,
)

non_zero_decimals = decimals.filter(lambda d: d != 0)


class Test_Money_Unrounded_Arithmetic_Operations:
    def test_init(self, money):
        unrounded = Money._Unrounded(money())
        assert unrounded.amount == Decimal("200")
        assert unrounded.currency == Currency.of("USD")

    @given(mny=_any_money_unrounded(), factor=decimals)
    def test_multiplication(self, mny, factor):
        result = mny * factor
        assert result.amount == mny.amount * factor
        assert result.amount == factor * mny.amount

    def test_multiplication_does_not_mutate_its_operand(self, money):
        unrounded = Money._Unrounded(money())
        original_amount = unrounded.amount
        _ = unrounded * Decimal("1.5")

        assert original_amount == unrounded.amount

    @given(mny=_any_money_unrounded(), factor=decimals)
    def test_implace_multiplication(self, mny, factor):
        expected_amount = mny.amount * factor
        mny *= factor

        assert mny.amount == expected_amount

    @given(mny=_any_money_unrounded(), left=decimals, right=decimals)
    def test_multiplication_is_associative_under_reasonable_input(
        self, mny, left, right
    ):
        # The range of inputs is encoded in the stategies
        # if the inputs are astronomically big, associativiy may break
        # du to implicit Decimal rounding to accomodate its context precision
        assert (mny * left) * right == mny * (left * right)

    def test_multiplication_rejects_negative_inputs(self, money):
        unrounded = Money._Unrounded(money())
        with pytest.raises(ValueError, match=f"expected non-negative factor, got {-2}"):
            _ = unrounded * Decimal("-2")

    @given(mny=_any_money_unrounded(), factor=non_zero_decimals)
    def test_division(self, mny, factor):
        result = mny / factor
        assert result.amount == mny.amount / factor

    def test_division_does_not_mutate_its_operand(self, money):
        unrounded = Money._Unrounded(money())
        original_amount = unrounded.amount
        _ = unrounded / Decimal("1.5")

        assert original_amount == unrounded.amount

    @given(mny=_any_money_unrounded(), factor=non_zero_decimals)
    def test_implace_division(self, mny, factor):
        expected_amount = mny.amount / factor
        mny /= factor

        assert mny.amount == expected_amount

    @given(mny=_any_money_unrounded())
    def test_division_by_one_return_the_same_amount(self, mny):
        result = mny / Decimal("1")
        assert result == mny

    def test_division_rejects_negative_inputs(self, money):
        unrounded = Money._Unrounded(money())
        with pytest.raises(ValueError, match=f"expected non-negative factor, got {-2}"):
            _ = unrounded / Decimal("-2")

    def test_division_by_zero_raise_division_error(self, money):
        unrounded = Money._Unrounded(money())
        with pytest.raises(ZeroDivisionError):
            _ = unrounded / Decimal("0")


class Test_Money_Unrounded_Quantize:
    def test_quantize_preserves_currency(self, money):
        unrounded = Money._Unrounded(money())
        assert unrounded.currency == money().currency

    @pytest.mark.parametrize(
        "amount, rounding, expected",
        [
            (Decimal("123.4"), RoundingPolicy.HALF_EVEN, 123),
            (Decimal("123.5"), RoundingPolicy.HALF_EVEN, 124),
            (Decimal("124.5"), RoundingPolicy.HALF_EVEN, 124),
            (Decimal("123.5"), RoundingPolicy.HALF_UP, 124),
            (Decimal("123.5"), RoundingPolicy.DOWN, 123),
        ],
    )
    def test_quantize_produce_expected_result(self, amount, rounding, expected, money):
        unrounded = Money._Unrounded(money())
        unrounded.amount = amount
        assert unrounded.quantize(rounding) == money(expected)

    @given(amount=st.integers(-(10**19), 10**19), rounding=rounding())
    def test_quantize_integer_is_independant_of_rounding(self, amount, rounding, money):
        unrounded = Money._Unrounded(money())
        unrounded.amount = Decimal(amount)
        assert unrounded.quantize() == money(amount)

    @given(n=st.integers(1, 100))
    def test_quantize_multiplying_by_integer(self, n, money):
        mny = money(20)
        assert (mny * Decimal(str(n))).quantize() == (
            sum((money(20) for i in range(n)), Money.zero("USD"))
        )

    @given(amount=st.integers(-(10**19), 10**19))
    def test_quantize_after_division_by_one_is_identity(self, amount, money):
        unrounded = money(amount) / Decimal("1")
        assert unrounded.quantize() == money(amount)


class Test_Money_Unrounded_Properties:
    def test_chained_operations_preserve_order(self, money):
        expr = ((money(299) * Decimal("15")) / Decimal("0.15")) * Decimal("25")

        expected = Decimal("299") * Decimal("15") / Decimal("0.15") * Decimal("25")

        assert expr.amount == expected

    def test_quantize_after_chained_operations(self, money):
        result = ((money(199) * Decimal("15")) / Decimal("0.25")).quantize()

        expected = Money.from_major(
            Decimal(199) * Decimal("15") / Decimal("0.25") / 10**2, "USD"
        )

        assert result == expected

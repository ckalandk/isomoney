from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering
from typing import Self, final

from isomoney.formatting import format as money_format

from ._decimal import _decimal_places
from .currency import Ccy, Currency
from .exceptions import CurrencyMismatchError
from .rounding import RoundingPolicy, as_decimal_rounding

__all__ = ["Money"]


@dataclass(frozen=True, slots=True)
class AllocationResult:
    shares: list[Money]
    remainder: Money


@total_ordering
@final
class Money:
    """
    Represents an immutable monetary amount in a specific ISO 4217 currency.

    Monetary amounts are stored internally as an integer number of minor units
    (for example, cents for USD). Arithmetic and comparison operations are only
    permitted between Money objects that share the same currency.
    Money instances are exact. No rounding is performed when constructing
    or manipulating monetary amounts.

    Parameters
    ----------
    minor_units : int
        The monetary amount expressed in the currency's minor units.
    currency : Currency
        The currency associated with the monetary amount.

    Notes
    -----
    The internal representation always uses minor units. For example:

    - Money(2934, currency=Currency(Ccy.USD)) represents 29.34 USD.
    - Money(29, currency=Currency(Ccy.JPY)) represents 29 JPY.
    """

    _amount: int
    _currency: Currency

    __slots__ = ("_amount", "_currency")

    _zero_cache: dict[str, Self] = {}

    def __new__(cls, minor_units: int, currency: Currency) -> Self:
        if minor_units == 0:
            if currency.ccy_code not in cls._zero_cache:
                instance = super().__new__(cls)
                cls._zero_cache[currency.ccy_code] = instance
            return cls._zero_cache[currency.ccy_code]
        return super().__new__(cls)

    def __init__(self, minor_units: int, currency: Currency) -> None:
        object.__setattr__(self, "_amount", minor_units)
        object.__setattr__(self, "_currency", currency)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} instances are immutable")

    @classmethod
    def zero(cls, currency: Ccy | str) -> Money:
        ccy = Currency.of(currency)
        return cls(0, ccy)

    @classmethod
    def from_major(
        cls,
        amount: Decimal | float,
        currency: Ccy | str,
        *,
        rounding: RoundingPolicy = RoundingPolicy.HALF_EVEN,
    ) -> Self:
        """
        Construct a Money instance from an amount expressed in major units.

        Parameters
        ----------
        amount : Decimal | float
            The monetary amount expressed in major units.
        currency : Ccy | str
            Either a member of the ``Ccy`` enumeration or a three-letter ISO 4217
            currency code.
        rounding: RoundingPolicy | None:
            The rounding policy if the decimal/float has more decimals then
            the currency supports
        Returns
        -------
        Money
            The corresponding Money instance.

        Raises
        ------
        ValueError If the amount contains more fractional digits than the currency
        supports and a the rounding policy is not supplied
        or if the amount is NaN or infinite.

        Examples
        --------
        >>> Money.from_major(Decimal("29.34"), "USD")
        Money(amount=2934, currency='USD')
        >>> Money.from_major(Decimal("29.345", "USD", rounding=RoundingPolicy.UP))
        Money(amount=2935, currency='USD')
        >>> Money.from_major(29.99, Ccy.USD)
        Money(amount=2999, currency='USD')
        """
        ccy = Currency.of(currency)
        decimal_amount = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        decimal_amount = cls._validate_amount(decimal_amount, ccy, rounding)
        minor_units = int(decimal_amount * (10**ccy.minor_units))
        return cls(minor_units, currency=ccy)

    @staticmethod
    def _validate_amount(
        amount: Decimal,
        currency: Currency,
        rounding: RoundingPolicy = RoundingPolicy.HALF_EVEN,
    ) -> Decimal:
        if not amount.is_finite():
            raise ValueError(f"Special/infinite values are forbidden: {amount}")
        exponent = _decimal_places(amount)
        if exponent > currency.minor_units:
            exp = Decimal(f"1.{'0' * currency.minor_units}")
            amount = amount.quantize(exp, rounding=as_decimal_rounding(rounding))
        return amount

    @property
    def currency(self) -> Currency:
        """
        The currency associated with this monetary amount.

        Returns
        -------
        Currency
            The Money object's currency.
        """
        return self._currency

    @property
    def minor_units(self) -> int:
        """
        The monetary amount expressed in minor units.

        Returns
        -------
        int
            The amount stored internally as an integer number of minor units.
        """
        return self._amount

    def allocate(
        self,
        ratios: Sequence[int],
    ) -> AllocationResult:
        total_weight = sum(ratios)
        shares = [
            Money(self._amount * ratio // total_weight, currency=self._currency)
            for ratio in ratios
        ]
        leftover = self - sum(shares, Money(0, self.currency))

        return AllocationResult(shares=shares, remainder=leftover)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented

        return self.currency == other.currency and self._amount == other._amount

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise CurrencyMismatchError(
                "Cannot compare money values with different currencies"
            )
        return self._amount < other._amount

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                "Cannot add money amounts with different currencies."
            )
        return Money(
            self._amount + other._amount,
            self.currency,
        )

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return self + (-other)

    def __neg__(self) -> Money:
        return Money(-self._amount, currency=self.currency)

    def __divmod__(self, divisor: int) -> tuple[Money, Money]:
        quot, rem = divmod(self._amount, divisor)
        return (Money(quot, currency=self.currency), Money(rem, currency=self.currency))

    def to_decimal(self) -> Decimal:
        """
        Convert the monetary amount to its major-unit representation.

        The returned Decimal always uses the exact number of fractional digits
        defined by the currency's minor units.

        Returns
        -------
        Decimal
            The amount expressed in major units.

        Examples
        --------
        >>> Money(2934, currency=Currency(Ccy.USD)).to_decimal()
        Decimal('29.34')
        >>> Money(29, currency=Currency(Ccy.JPY)).to_decimal()
        Decimal('29')
        >>> Money(29123, currency=Currency(Ccy.KWD)).to_decimal()
        Decimal('29.123')
        """
        mn_unit = self.currency.minor_units
        if mn_unit == 0:
            exponent = Decimal("1")
        else:
            exponent = Decimal(f"1e-{mn_unit}")
        ret = Decimal(self._amount) * exponent
        return ret

    def __repr__(self) -> str:
        return f"Money(amount={self.to_decimal()}, currency='{self.currency.ccy_code}')"

    def __str__(self) -> str:
        return f"{self.to_decimal()} {self.currency.ccy_code}"

    def __format__(self, format_spec: str) -> str:
        """
        Format the monetary amount.

        Format specification grammar
        ----------------------------

        money-format ::= money-spec string-format

        money-spec ::= [display] [compact] [accounting] [ungroup]

        display ::= h | i | n
        compact ::= c
        accounting ::= a
        ungroup ::= u

        Display options
        ---------------

        h
            Hide the currency.

        i
            Display the ISO 4217 currency code.

        n
            Display the currency name.

        c
            Use compact notation (for example, ``1.2M``).

        a
            Display negative amounts using accounting notation
            (for example, ``(123.45)`` instead of ``-123.45``).

        u
            Disable digit grouping (for example, ``1000000`` instead of
            ``1,000,000``).

        string-format
        -------------

        Python's standard string format specification. It is applied after the
        money-specific options.

        Examples
        --------

        >>> f"{money:}"
        >>> f"{money:h}"
        >>> f"{money:hc}"
        >>> f"{money:ia}"
        >>> f"{money:hc>20}"
        """
        return money_format(self, format_spec)

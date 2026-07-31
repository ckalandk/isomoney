from decimal import Decimal
from functools import total_ordering
from typing import Self, final
from .currency import Ccy, Currency

__all__ = ["Money"]


def _decimal_places(x: Decimal) -> int:
    digits = x.as_tuple().digits
    exponent = x.as_tuple().exponent

    assert isinstance(exponent, int) #Shut up type checker
    if exponent >= 0:
        return 0

    fractional_digits = digits[exponent:]
    counter = abs(exponent)
    while counter >= 0 and fractional_digits[counter - 1] == 0:
        counter -= 1

    return counter


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

    def __init__(self, minor_units: int, *, currency: Currency):
        object.__setattr__(self, "_amount", minor_units)
        object.__setattr__(self, "_currency", currency)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} instances are immutable")

    @classmethod
    def from_major(cls, amount: Decimal | float, currency: Ccy | str) -> Self:
        """
        Construct a Money instance from an amount expressed in major units.

        Parameters
        ----------
        amount : Decimal | float
            The monetary amount expressed in major units.
        currency : Ccy | str
            Either a member of the ``Ccy`` enumeration or a three-letter ISO 4217
            currency code.

        Returns
        -------
        Money
            The corresponding Money instance.

        Raises
        ------
        ValueError If the amount contains more fractional digits than the currency
        supports or if the amount is NaN or infinite.

        Examples
        --------
        >>> Money.from_major(Decimal("29.34"), "USD")
        Money(amount=2934, currency=Currency(ccy='USD'))
        >>> Money.from_major(29.99, Ccy.USD)
        Money(amount=2999, currency=Currency(ccy='USD'))
        """
        ccy = Currency.of(currency)
        decimal_amount = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        cls._validate_amount(decimal_amount, ccy)
        minor_units = int(decimal_amount * (10**ccy.minor_units))
        return cls(minor_units, currency=ccy)

    @staticmethod
    def _validate_amount(amount: Decimal, currency: Currency) -> None:
        if not amount.is_finite():
            raise ValueError(f"Special/infinite values are forbidden: {amount}")
        exponent = _decimal_places(amount)
        if exponent > currency.minor_units:
            raise ValueError(
                f'"{currency.ccy_code}" support only {currency.minor_units} minor units'
            )

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented

        return self.currency == other.currency and self._amount == other._amount

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise ValueError("Cannot compare money values with different currencies")
        return self._amount < other._amount

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot add money amounts with different currencies.")
        return Money(
            self._amount + other._amount,
            currency=self.currency,
        )

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return self + (-other)

    def __neg__(self) -> Money:
        return Money(-self._amount, currency=self.currency)

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
        return ret.quantize(exponent)

    def __repr__(self) -> str:
        return f"Money(amount={self._amount}, currency={self.currency})"

    def __str__(self) -> str:
        return f"{self.to_decimal()} {self.currency.ccy_code}"

    def __format__(self, format_spec: str) -> str:
        return repr(self)

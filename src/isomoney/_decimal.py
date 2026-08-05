from decimal import Decimal

from isomoney.rounding import RoundingPolicy, as_decimal_rounding


def _decimal_places(x: Decimal) -> int:
    """
    Return the number of significant decimal places in a Decimal number.
    """
    digits = x.as_tuple().digits
    exponent = x.as_tuple().exponent

    assert isinstance(exponent, int)  # Shut up type checker
    if exponent >= 0:
        return 0

    fractional_digits = digits[exponent:]
    counter = abs(exponent)
    while counter >= 0 and fractional_digits[counter - 1] == 0:
        counter -= 1

    return counter


def _remove_trailing_zeros(value: Decimal, precision: int = 2) -> Decimal:
    """
    Removes trailing fractional zeroes from a Decimal .
    """
    if value == value.to_integral():
        cleaned = value.quantize(Decimal("1"))
    else:
        cleaned = value.normalize()
    return cleaned


def _enforce_precision(
    value: Decimal, precision: int, rounding: RoundingPolicy
) -> Decimal:
    return value.quantize(
        Decimal(f"1.{'0' * precision}"), rounding=as_decimal_rounding(rounding)
    )


def _force_decimal(value: float | Decimal) -> Decimal:
    if not isinstance(value, Decimal):
        return Decimal(str(value))
    return value

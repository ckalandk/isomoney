from decimal import Decimal


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

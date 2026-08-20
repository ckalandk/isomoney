import decimal
from enum import Enum, auto

__all__ = ["RoundingMode"]


class RoundingMode(Enum):
    CEILING = auto()
    FLOOR = auto()
    DOWN = auto()
    UP = auto()
    HALF_EVEN = auto()
    HALF_DOWN = auto()
    HALF_UP = auto()
    HALF_ODD = auto()
    HALF_CEILING = auto()
    HALF_FLOOR = auto()
    UNNECESSARY = auto()


def as_decimal_rounding(policy: RoundingMode) -> str:
    """Map rounding from RoundingMode enum to python Decimal rounding"""
    _decimal_map = {
        RoundingMode.CEILING: decimal.ROUND_CEILING,
        RoundingMode.FLOOR: decimal.ROUND_FLOOR,
        RoundingMode.DOWN: decimal.ROUND_DOWN,
        RoundingMode.UP: decimal.ROUND_UP,
        RoundingMode.HALF_EVEN: decimal.ROUND_HALF_EVEN,
        RoundingMode.HALF_DOWN: decimal.ROUND_HALF_DOWN,
        RoundingMode.HALF_UP: decimal.ROUND_HALF_UP,
    }
    try:
        return _decimal_map[policy]
    except KeyError:
        raise NotImplementedError(
            f"{policy.name} is not supported by the decimal backend."
        ) from None

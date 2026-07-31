from enum import Enum, auto
import decimal

class RoundingPolicy(Enum):
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


def to_decimal(policy: RoundingPolicy):
    _decimal_map = {
        RoundingPolicy.CEILING: decimal.ROUND_CEILING,
        RoundingPolicy.FLOOR: decimal.ROUND_FLOOR,
        RoundingPolicy.DOWN: decimal.ROUND_DOWN,
        RoundingPolicy.UP: decimal.ROUND_UP,
        RoundingPolicy.HALF_EVEN: decimal.ROUND_HALF_EVEN,
        RoundingPolicy.HALF_DOWN: decimal.ROUND_HALF_DOWN,
        RoundingPolicy.HALF_UP: decimal.ROUND_HALF_UP,
    }
    try:
        return _decimal_map[policy]
    except KeyError:
        raise NotImplementedError(
            f"{policy.name} is not supported by the decimal backend."
        )


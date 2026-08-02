from dataclasses import dataclass
from typing import Literal, TypeGuard

Display = Literal["hidden", "symbol", "iso", "name"]

def _is_display(value: str) -> TypeGuard[Display]:
    return value in ("hidden", "symbol", "iso", "name")

@dataclass(frozen=True, slots=True, kw_only=True)
class FormatSpec:
    compact: bool = False
    accounting: bool = False
    group_separator: bool = True

    ccy_display: Display = "symbol"
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True, slots=True, kw_only=True)
class FormatSpec:
    compact: bool = False
    accounting: bool = False
    group_separator: bool = True

    ccy_display: Literal["hidden", "symbol", "iso", "name"] = "symbol"
from dataclasses import dataclass
from typing import Literal

DisplayOpts = Literal["hidden", "symbol", "iso", "name"]


@dataclass(slots=True)
class FormatSpec:
    ccy_display: DisplayOpts = "symbol"

    compact: bool = False
    compact_precision: int | None = 1
    accounting: bool = False
    group_separator: bool = True

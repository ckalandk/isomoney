import decimal

import icu  # pyright: ignore[reportMissingImports]

from isomoney.exceptions import InvalidFormatSpecError
from isomoney.rounding import RoundingPolicy

from .base_formatter import CcyFormatter
from .formatspec import FormatSpec

_icu_rounding_map = {
    RoundingPolicy.CEILING: icu.DecimalFormat.kRoundCeiling,  #
    RoundingPolicy.FLOOR: icu.DecimalFormat.kRoundFloor,  #
    RoundingPolicy.DOWN: icu.DecimalFormat.kRoundDown,  #
    RoundingPolicy.UP: icu.DecimalFormat.kRoundUp,  #
    RoundingPolicy.HALF_EVEN: icu.DecimalFormat.kRoundHalfEven,  #
    RoundingPolicy.HALF_DOWN: icu.DecimalFormat.kRoundHalfDown,  #
    RoundingPolicy.HALF_UP: icu.DecimalFormat.kRoundHalfUp,  #
    RoundingPolicy.HALF_ODD: icu.UNumberFormatRoundingMode.HALF_ODD,
    RoundingPolicy.HALF_CEILING: icu.UNumberFormatRoundingMode.HALF_CEILING,
    RoundingPolicy.HALF_FLOOR: icu.UNumberFormatRoundingMode.HALF_FLOOR,
    RoundingPolicy.UNNECESSARY: icu.UNumberFormatRoundingMode.UNNECESSARY,
}


def _build_icu_currency_formatter(
    currency: str,
    locale: str,
    ctx: FormatSpec,
    precision: int = 2,
    rounding: RoundingPolicy = RoundingPolicy.HALF_EVEN,
    omit_trailing_zeros: bool = False,
) -> icu.NumberFormatter:
    """
    Returns an ICU NumberFormatter configured for specific financial layouts.
    """
    if ctx.ccy_display == "name" and ctx.accounting:
        raise InvalidFormatSpecError(
            "Accounting format is not supported with currency name display."
        )

    # Common Formatter Setup
    formatter = icu.NumberFormatter.withLocale(icu.Locale(locale)).unit(
        icu.CurrencyUnit(currency)
    )

    # Apply  Currency Display
    display_widths = {
        "hidden": icu.UNumberUnitWidth.HIDDEN,
        "symbol": icu.UNumberUnitWidth.SHORT,
        "iso": icu.UNumberUnitWidth.ISO_CODE,
        "name": icu.UNumberUnitWidth.FULL_NAME,
    }

    assert ctx.ccy_display in display_widths

    formatter = formatter.unitWidth(display_widths[ctx.ccy_display])

    # Apply Number Presentation
    if ctx.accounting:
        formatter = formatter.sign(icu.UNumberSignDisplay.ACCOUNTING)
    else:
        formatter = formatter.sign(icu.UNumberSignDisplay.AUTO)

    if ctx.compact:
        formatter = formatter.notation(icu.Notation.compactShort())

    # Apply Precision & Trailing Zeros
    if omit_trailing_zeros:
        precision_rule = icu.Precision.minMaxFraction(0, precision)
    else:
        precision_rule = icu.Precision.fixedFraction(precision)

    formatter = formatter.precision(precision_rule)

    # Apply Decimal Rounding Strategy
    try:
        icu_rounding = _icu_rounding_map[rounding]
    except KeyError:
        raise AssertionError(f"Missing ICU mapping for {rounding}") from None
    formatter = formatter.roundingMode(icu_rounding)

    # Apply Group Separator
    if not ctx.group_separator:
        formatter = formatter.grouping(icu.UNumberGroupingStrategy.OFF)
    else:
        formatter = formatter.grouping(icu.UNumberGroupingStrategy.AUTO)

    return formatter


class IcuFormatter(CcyFormatter):
    def __init__(self, locale: str = "") -> None:
        self._locale = locale if locale else str(icu.Locale.getDefault())
        self.ctx = FormatSpec(
            compact=False, accounting=False, group_separator=True, ccy_display="symbol"
        )

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value

    def format(
        self,
        amount: decimal.Decimal,
        currency: str,
        ctx: FormatSpec,
        *,
        precision: int,
        rounding: RoundingPolicy,
        omit_trailing_zeros: bool,
    ) -> str:
        formatter = _build_icu_currency_formatter(
            currency, self.locale, ctx, precision, rounding, omit_trailing_zeros
        )
        if ctx.accounting and ctx.compact and amount < 0:
            # ICU/CLDR does not define accounting formatting for compact notation.
            # We emulate it by formatting the absolute value and surrounding it
            # with parentheses. we strip the result to avoid extra spaces that may arise
            # when the currency symbol is hidden
            # TODO: This needs to be extensively tested across locales to ensure
            # it behaves as expected.
            positive_string = formatter.formatDecimal(str(abs(amount)).encode("utf-8"))
            return f"({positive_string.strip()})"
        # The returned formatted string i stripped from leading/trailing whitespace
        # to avoid issues with hidden currency symbols and compact formatting.
        return formatter.formatDecimal(str(amount).encode("utf-8")).strip()  # type: ignore[no-any-return]

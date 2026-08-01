from .protocols import CcyFormatter
from isomoney.rounding import RoundingPolicy
from .formatspec import FormatSpec
import icu
import decimal

_icu_rounding_map = {
    RoundingPolicy.CEILING: icu.DecimalFormat.kRoundCeiling,#
    RoundingPolicy.FLOOR: icu.DecimalFormat.kRoundFloor,#
    RoundingPolicy.DOWN: icu.DecimalFormat.kRoundDown,#
    RoundingPolicy.UP: icu.DecimalFormat.kRoundUp,#
    RoundingPolicy.HALF_EVEN: icu.DecimalFormat.kRoundHalfEven,#
    RoundingPolicy.HALF_DOWN: icu.DecimalFormat.kRoundHalfDown,#
    RoundingPolicy.HALF_UP: icu.DecimalFormat.kRoundHalfUp,#
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
):
    """
    Returns an ICU NumberFormatter configured for specific financial layouts.
    """
    if ctx.ccy_display == "name" and ctx.accounting:
            raise ValueError()
    
    # Common Formatter Setup
    formatter = (
        icu.NumberFormatter.withLocale(icu.Locale(locale))
        .unit(icu.CurrencyUnit(currency))
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
        raise AssertionError(
            f"Missing ICU mapping for {rounding}"
        )
    formatter = formatter.roundingMode(icu_rounding)

    # Apply Group Separator
    if not ctx.group_separator:
        formatter = formatter.grouping(icu.UNumberGroupingStrategy.OFF)
    else:
        formatter = formatter.grouping(icu.UNumberGroupingStrategy.AUTO)

    return formatter
    

class IcuFormatter(CcyFormatter):
    def __init__(self, locale: str|None = None) -> None:
        self.locale = locale if locale else str(icu.Locale.getDefault())

    def format(
        self, 
        amount: decimal.Decimal,
        currency:str, 
        ctx: FormatSpec, 
        precision:int = 2, 
        rounding: str = RoundingPolicy.HALF_EVEN, 
        omit_trailing_zeros:bool = False
    ) -> str:
        formatter = _build_icu_currency_formatter(
            currency,
            self.locale,
            ctx,
            precision,
            rounding,
            omit_trailing_zeros
        )
        if ctx.accounting and ctx.compact and amount < 0:
            # ICU/CLDR does not define accounting formatting for compact notation.
            # We emulate it by formatting the absolute value and surrounding it
            # with parentheses.
            positive_string = formatter.formatDecimal(str(abs(amount)).encode('utf-8'))
            return f"({positive_string})"
        return formatter.formatDecimal(str(amount).encode('utf-8'))

        
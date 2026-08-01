import pytest
from isomoney.formatting import IcuFormatter, FormatSpec
from decimal import Decimal
from isomoney import InvalidFormatSpecError
from isomoney.rounding import RoundingPolicy

def normalize_space(s: str) -> str:
    """Helper to convert ICU non-breaking spaces into regular spaces for easier assertions."""
    return s.replace('\xa0', ' ').replace('\u202f', ' ').strip()


class TestIcuFormatter:
    
    @pytest.fixture
    def usd_formatter(self):
        return IcuFormatter(locale="en_US")
        
    @pytest.fixture
    def eur_formatter_fr(self):
        return IcuFormatter(locale="fr_FR")

    # --- 1. Basic Currency Display Tests ---
    
    @pytest.mark.parametrize("display, amount, expected", [
        ("symbol", Decimal("1234.56"), "$1,234.56"),
        ("hidden", Decimal("1234.56"), "1,234.56"),
        ("iso", Decimal("1234.56"), "USD 1,234.56"),
        ("name", Decimal("1234.56"), "1,234.56 US dollars"),
    ])
    def test_currency_display_widths(self, usd_formatter, display, amount, expected):
        ctx = FormatSpec(ccy_display=display)
        result = usd_formatter.format(amount, "USD", ctx)
        assert normalize_space(result) == expected

    def test_invalid_display_width_raises_error(self, usd_formatter):
        ctx = FormatSpec(ccy_display="invalid_type")
        with pytest.raises(AssertionError):
            usd_formatter.format(Decimal("100"), "USD", ctx)

    def test_name_and_accounting_raises_value_error(self, usd_formatter):
        ctx = FormatSpec(ccy_display="name", accounting=True)
        with pytest.raises(ValueError):
            usd_formatter.format(Decimal("-100"), "USD", ctx)

    # --- 2. Accounting Sign Tests ---
    
    @pytest.mark.parametrize("amount, accounting, expected", [
        (Decimal("-1234.56"), False, "-$1,234.56"),  # Standard Negative
        (Decimal("-1234.56"), True, "($1,234.56)"),  # Accounting Negative
        (Decimal("1234.56"), True, "$1,234.56"),     # Accounting Positive (no parens)
    ])
    def test_accounting_format(self, usd_formatter, amount, accounting, expected):
        ctx = FormatSpec(accounting=accounting)
        result = usd_formatter.format(amount, "USD", ctx)
        assert normalize_space(result) == expected

    # --- 3. Compact Notation Tests ---
    
    @pytest.mark.parametrize("amount, expected", [
        (Decimal("1500"), "$1.5K"),
        (Decimal("1500000"), "$1.5M"),
        (Decimal("1500000000"), "$1.5B"),
    ])
    def test_compact_notation_positive(self, usd_formatter, amount, expected):
        ctx = FormatSpec(compact=True)
        # Using precision=1 to explicitly show the first decimal in compact form
        result = usd_formatter.format(amount, "USD", ctx, precision=1)
        assert normalize_space(result) == expected

    def test_compact_accounting_negative_workaround(self, usd_formatter):
        """Tests the specific hack ensuring CLDR supports compact + accounting for negatives"""
        ctx = FormatSpec(compact=True, accounting=True)
        amount = Decimal("-2500000")
        
        result = usd_formatter.format(amount, "USD", ctx, precision=1)
        
        # Without the workaround, this would typically render as -$2.5M
        assert normalize_space(result) == "($2.5M)"

    # --- 4. Precision and Trailing Zeros ---
    
    @pytest.mark.parametrize("amount, precision, omit_zeros, expected", [
        (Decimal("12.50"), 2, False, "$12.50"), # Fixed precision
        (Decimal("12.50"), 2, True, "$12.5"),   # Strips trailing zero
        (Decimal("12.00"), 2, True, "$12"),     # Strips all decimals
        (Decimal("12.345"), 1, False, "$12.3"), # Cuts off at precision 1
        (Decimal("12.345"), 4, False, "$12.3450"), # Pads up to precision 4
    ])
    def test_precision_and_trailing_zeros(self, usd_formatter, amount, precision, omit_zeros, expected):
        ctx = FormatSpec()
        result = usd_formatter.format(amount, "USD", ctx, precision=precision, omit_trailing_zeros=omit_zeros)
        assert normalize_space(result) == expected

    # --- 5. Grouping Separators ---
    
    @pytest.mark.parametrize("group_sep, expected", [
        (True, "$1,234,567.89"),
        (False, "$1234567.89"),
    ])
    def test_group_separator(self, usd_formatter, group_sep, expected):
        ctx = FormatSpec(group_separator=group_sep)
        result = usd_formatter.format(Decimal("1234567.89"), "USD", ctx)
        assert normalize_space(result) == expected

    # --- 6. Rounding Policies ---
    
    @pytest.mark.parametrize("amount, policy, expected", [
        (Decimal("12.345"), RoundingPolicy.DOWN, "$12.34"),      # Truncate
        (Decimal("12.345"), RoundingPolicy.UP, "$12.35"),        # Away from zero
        (Decimal("12.345"), RoundingPolicy.HALF_EVEN, "$12.34"), # Banker's rounding (even)
        (Decimal("12.355"), RoundingPolicy.HALF_EVEN, "$12.36"), # Banker's rounding (even)
        (Decimal("12.345"), RoundingPolicy.HALF_UP, "$12.35"),   # Standard math round
    ])
    def test_rounding_policies(self, usd_formatter, amount, policy, expected):
        ctx = FormatSpec()
        result = usd_formatter.format(amount, "USD", ctx, precision=2, rounding=policy)
        assert normalize_space(result) == expected

    def test_invalid_rounding_policy_raises(self, usd_formatter):
        ctx = FormatSpec()
        with pytest.raises(AssertionError): 
            # Forcing an invalid mapping
            usd_formatter.format(Decimal("100"), "USD", ctx, rounding="NON_EXISTENT")

    # --- 7. Cross-Locale Verification ---
    
    def test_french_locale_formatting(self, eur_formatter_fr):
        """Ensures that layout/sign configurations respect the locale's native positioning."""

        # Standard
        ctx = FormatSpec(group_separator=True)
        res_std = eur_formatter_fr.format(Decimal("1234.56"), "EUR", ctx)
        assert normalize_space(res_std) == "1 234,56 €"
        
        # Accounting Negative
        ctx_acc = FormatSpec(accounting=True)
        res_acc = eur_formatter_fr.format(Decimal("-1234.56"), "EUR", ctx_acc)
        # Assuming French accounting wraps the whole string
        assert normalize_space(res_acc) == "(1 234,56 €)" 
        
        # Compact Accounting Negative Workaround
        ctx_comp = FormatSpec(accounting=True, compact=True)
        res_comp = eur_formatter_fr.format(Decimal("-1500000"),"EUR", ctx_comp, precision=1)
        assert normalize_space(res_comp) == "(1,5 M €)"
from decimal import Decimal
from functools import partial

import pytest

from isomoney.exceptions import InvalidFormatSpecError
from isomoney.formatting.formatspec import FormatSpec
from isomoney.formatting.std_formatter import StdFormatter
from isomoney.rounding import RoundingPolicy


class TestStdFormatter:
    @pytest.fixture
    def std_formatter(self):
        fmt = StdFormatter()
        _format = partial(
            fmt.format,
            precision=2,
            rounding=RoundingPolicy.HALF_EVEN,
            omit_trailing_zeros=False,
        )
        fmt.format = _format 
        return fmt

    # Basic Currency Display Tests

    @pytest.mark.parametrize(
        "display, amount, expected",
        [
            ("hidden", Decimal("1234.56"), "1,234.56"),
            ("iso", Decimal("1234.56"), "1,234.56 USD"),
            ("name", Decimal("1234.56"), "1,234.56 US Dollar"),
        ],
    )
    def test_currency_display_widths(self, std_formatter, display, amount, expected):
        ctx = FormatSpec(ccy_display=display)
        result = std_formatter.format(amount, "USD", ctx)
        assert result == expected

    def test_invalid_display_width_raises_error(self, std_formatter):
        ctx = FormatSpec(ccy_display="invalid_type")  # type: ignore
        with pytest.raises(AssertionError):
            std_formatter.format(Decimal("100"), "USD", ctx)

    def test_symbol_raises_invalid_format_spec_error(self, std_formatter):
        ctx = FormatSpec(ccy_display="symbol")
        with pytest.raises(InvalidFormatSpecError):
            std_formatter.format(Decimal("-100"), "USD", ctx)

    # Accounting Sign Tests

    @pytest.mark.parametrize(
        "amount, accounting, expected",
        [
            (Decimal("-1234.56"), False, "-1,234.56"),  # Standard Negative
            (Decimal("-1234.56"), True, "(1,234.56)"),  # Accounting Negative
            (Decimal("1234.56"), True, "1,234.56"),  # Accounting Positive (no parens)
        ],
    )
    def test_accounting_format(self, std_formatter, amount, accounting, expected):
        ctx = FormatSpec(accounting=accounting, ccy_display="hidden")
        result = std_formatter.format(amount, "USD", ctx)
        assert result == expected

    # Compact Notation Tests

    @pytest.mark.parametrize(
        "amount, expected",
        [
            (Decimal("1500"), "1.5K USD"),
            (Decimal("1500000"), "1.5M USD"),
            (Decimal("1500000000"), "1.5B USD"),
        ],
    )
    def test_compact_notation_positive(self, std_formatter, amount, expected):
        ctx = FormatSpec(compact=True, ccy_display="iso")
        # Using precision=1 to explicitly show the first decimal in compact form
        result = std_formatter.format(amount, "USD", ctx, precision=1)
        assert result == expected

    @pytest.mark.parametrize(
            "amount,ccy_display,expected", [
                (Decimal('-2500000'), "iso", "(2.5M USD)"),
                (Decimal('-2500000'), "hidden", "(2.5M)"),
                (Decimal('-2500000'), "name", "(2.5M US Dollar)"),
            ],
    )
    def test_compact_accounting_negative(
        self, std_formatter, amount, ccy_display, expected
        ):
       
        ctx = FormatSpec(compact=True, accounting=True, ccy_display=ccy_display)
        result = std_formatter.format(amount, "USD", ctx, precision=1)

        assert result == expected

    # Precision and Trailing Zeros

    # @pytest.mark.parametrize(
    #     "amount, precision, omit_zeros, expected",
    #     [
    #         (Decimal("12.50"), 2, False, "12.50"), 
    #         (Decimal("12.50"), 2, True, "12.5"),  
    #         (Decimal("12.00"), 2, True, "12.00"),  
    #         (Decimal("12.345"), 1, False, "12.3"),  
    #         (Decimal("12.345"), 4, False, "12.3450"),
    #     ],
    # )
    # def test_precision_and_trailing_zeros(
    #     self, std_formatter, amount, precision, omit_zeros, expected
    # ):
    #     ctx = FormatSpec(ccy_display="hidden")
    #     result = std_formatter.format(
    #         amount, "USD", ctx, precision=precision, omit_trailing_zeros=omit_zeros
    #     )
    #     assert result == expected

    # # Grouping Separators

    # @pytest.mark.parametrize(
    #     "group_sep, expected",
    #     [
    #         (True, "$1,234,567.89"),
    #         (False, "$1234567.89"),
    #     ],
    # )
    # def test_group_separator(self, std_formatter, group_sep, expected):
    #     ctx = FormatSpec(group_separator=group_sep)
    #     result = std_formatter.format(Decimal("1234567.89"), "USD", ctx)
    #     assert normalize_space(result) == expected

    # # Rounding Policies

    # @pytest.mark.parametrize(
    #     "amount, policy, expected",
    #     [
    #         (Decimal("12.345"), RoundingPolicy.DOWN, "$12.34"),  # Truncate
    #         (Decimal("12.345"), RoundingPolicy.UP, "$12.35"),  # Away from zero
    #         (
    #             Decimal("12.345"),
    #             RoundingPolicy.HALF_EVEN,
    #             "$12.34",
    #         ),  # Banker's rounding (even)
    #         (
    #             Decimal("12.355"),
    #             RoundingPolicy.HALF_EVEN,
    #             "$12.36",
    #         ),  # Banker's rounding (even)
    #         (
    #             Decimal("12.345"),
    #             RoundingPolicy.HALF_UP,
    #             "$12.35",
    #         ),  # Standard math round
    #     ],
    # )
    # def test_rounding_policies(self, std_formatter, amount, policy, expected):
    #     ctx = FormatSpec()
    #     result = std_formatter.format(amount, "USD", ctx, precision=2, rounding=policy)
    #     assert normalize_space(result) == expected

    # def test_invalid_rounding_policy_raises(self, std_formatter):
    #     ctx = FormatSpec()
    #     with pytest.raises(AssertionError):
    #         std_formatter.format(Decimal("100"), "USD", ctx, rounding="NON_EXISTENT")

    # # Cross-Locale Verification using French Locale

    # def test_french_locale_formatting(self, eur_formatter_fr):
    #     """
    #     Ensures that layout/sign configurations respect
    #     the locale's native positioning.
    #     """

    #     # Standard
    #     ctx = FormatSpec(group_separator=True)
    #     res_std = eur_formatter_fr.format(Decimal("1234.56"), "EUR", ctx)
    #     assert normalize_space(res_std) == "1 234,56 €"

    #     # Accounting Negative
    #     ctx_acc = FormatSpec(accounting=True)
    #     res_acc = eur_formatter_fr.format(Decimal("-1234.56"), "EUR", ctx_acc)
    #     # Assuming French accounting wraps the whole string
    #     assert normalize_space(res_acc) == "(1 234,56 €)"

    #     # Compact Accounting Negative Workaround
    #     ctx_comp = FormatSpec(accounting=True, compact=True)
    #     res_comp = eur_formatter_fr.format(
    #         Decimal("-1500000"), "EUR", ctx_comp, precision=1
    #     )
    #     assert normalize_space(res_comp) == "(1,5 M €)"

    #     # compact with negative amount andhidden symbol
    #     ctx_comp_hidden = FormatSpec(
    #         accounting=True, compact=True, ccy_display="hidden"
    #     )
    #     res_comp_hidden = eur_formatter_fr.format(
    #         Decimal("-1500000000"), "EUR", ctx_comp_hidden, precision=1
    #     )
    #     assert normalize_space(res_comp_hidden) == "(1,5 Md)"

    #     # compact with positive amount andhidden symbol
    #     ctx_comp_hidden = FormatSpec(
    #         accounting=True, compact=True, ccy_display="hidden"
    #     )
    #     res_comp_hidden = eur_formatter_fr.format(
    #         Decimal("1500000000"), "EUR", ctx_comp_hidden, precision=1
    #     )
    #     assert normalize_space(res_comp_hidden) == "1,5 Md"

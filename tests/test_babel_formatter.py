from decimal import Decimal

import pytest

from pycents.exceptions import BackendConfigurationError, InvalidFormatSpecError
from pycents.formatting.babel import BabelFormatter
from pycents.formatting.formatspec import FormatSpec
from pycents.rounding import RoundingMode


class TestBabelFormatter:
    @pytest.fixture
    def babel_formatter(self):
        fmt = BabelFormatter("en_US")
        return fmt

    def test_init(self):
        _babel = BabelFormatter("en_US")
        assert _babel.locale == "en_US"
        assert _babel.numbering_system is None
        assert _babel._rounding == RoundingMode.HALF_EVEN
        assert _babel._default_spec == FormatSpec()

    def test_init_with_empty_local(self):
        _babel = BabelFormatter("")
        assert len(_babel.locale) > 0

    def test_locale_property(self, babel_formatter):
        assert babel_formatter.locale == "en_US"
        babel_formatter.locale = "fr_FR"
        assert babel_formatter.locale == "fr_FR"

    @pytest.mark.parametrize(
        "display, amount, expected",
        [
            ("hidden", Decimal("1234.56"), "1,234.56"),
            ("symbol", Decimal("12.9923"), "$12.9923"),
            ("iso", Decimal("1234.56"), "USD\xa01,234.56"),
            ("name", Decimal("1234.56"), "1,234.56 US dollars"),
        ],
    )
    def test_currency_display_widths(self, babel_formatter, display, amount, expected):
        spec = FormatSpec(ccy_display=display)
        result = babel_formatter.format(amount, "USD", spec)
        assert result == expected

    def test_invalid_display_width_raises_error(self, babel_formatter):
        spec = FormatSpec(ccy_display="invalid_type")  # type: ignore
        with pytest.raises(AssertionError):
            babel_formatter.format(Decimal("100"), "USD", spec)

    def test_name_display_and_accounting_raises_error(self, babel_formatter):
        spec = FormatSpec(ccy_display="name", accounting=True)
        with pytest.raises(
            InvalidFormatSpecError,
            match="Cannot display currency name while using accounting format.",
        ):
            babel_formatter.format(Decimal("-2.99"), "USD", spec)

    def test_name_display_with_compact_format(self, babel_formatter):
        spec = FormatSpec(ccy_display="name", compact=True)
        result = babel_formatter.format(Decimal("1222"), "USD", spec)

        assert result == "1.2K US dollars"

    def test_formatter_rejects_combining_compact_and_accounting_formats(
        self, babel_formatter
    ):
        spec = FormatSpec(accounting=True, compact=True)
        with pytest.raises(
            InvalidFormatSpecError,
            match="Cannot mix compact and accounting format display",
        ):
            babel_formatter.format(Decimal("2.99"), "USD", spec)

    # Accounting Sign Tests

    @pytest.mark.parametrize(
        "amount, accounting, expected",
        [
            (Decimal("-1232.56"), False, "-1,232.56"),  # Standard Negative
            (Decimal("-1233.56"), True, "(1,233.56)"),  # Accounting Negative
            (Decimal("1234.56"), True, "1,234.56"),  # Accounting Positive (no parens)
        ],
    )
    def test_accounting_format(self, babel_formatter, amount, accounting, expected):
        ctx = FormatSpec(accounting=accounting, ccy_display="hidden")
        result = babel_formatter.format(amount, "USD", ctx)
        assert result == expected

    # Compact Notation Tests

    @pytest.mark.parametrize(
        "amount, expected",
        [
            (Decimal("1500"), "USD\xa01.5K"),
            (Decimal("1500000"), "USD\xa01.5M"),
            (Decimal("1500000000"), "USD\xa01.5B"),
        ],
    )
    def test_compact_notation_positive(self, babel_formatter, amount, expected):
        spec = FormatSpec(compact=True, ccy_display="iso")
        result = babel_formatter.format(amount, "USD", spec)
        assert result == expected

    # Grouping Separators

    @pytest.mark.parametrize(
        "group_sep, expected",
        [
            (True, "1,234,567.89"),
            (False, "1234567.89"),
        ],
    )
    def test_group_separator(self, babel_formatter, group_sep, expected):
        spec = FormatSpec(group_separator=group_sep, ccy_display="hidden")
        result = babel_formatter.format(Decimal("1234567.89"), "USD", spec)
        assert result == expected

    # Rounding Policies

    @pytest.mark.parametrize(
        "amount, display, rounding, expected",
        [
            (Decimal("12340"), "symbol", RoundingMode.DOWN, "$12.34K"),
            (Decimal("12345"), "hidden", RoundingMode.UP, "12.35K"),
            (
                Decimal("12345"),
                "iso",
                RoundingMode.HALF_EVEN,
                "USD\xa012.34K",
            ),
            (
                Decimal("12355"),
                "symbol",
                RoundingMode.HALF_EVEN,
                "$12.36K",
            ),
            (
                Decimal("12345"),
                "name",
                RoundingMode.HALF_UP,
                "12.35K US dollars",
            ),
        ],
    )
    def test_rounding_policies(
        self, babel_formatter, amount, display, rounding, expected
    ):
        spec = FormatSpec(ccy_display=display, compact=True, compact_precision=2)
        babel_formatter.configure(rounding=rounding)
        result = babel_formatter.format(amount, "USD", spec)
        assert result == expected

    def test_configure(self, babel_formatter):
        babel_formatter.configure(
            compact=True, compact_precision=3, accounting=True, group_separator=False
        )
        expected = FormatSpec(
            ccy_display="symbol",
            compact=True,
            compact_precision=3,
            accounting=True,
            group_separator=False,
        )

        assert babel_formatter._default_spec == expected

    def test_system_numbering(self, babel_formatter):
        babel_formatter.locale = "en_US"
        result = babel_formatter.format(Decimal("1099.98"), "USD", FormatSpec())
        assert result == "$1,099.98"

        babel_formatter.locale = "ar_EG"
        babel_formatter.numbering_system = "default"
        result = babel_formatter.format(Decimal("1099.98"), "USD", FormatSpec())
        assert result == "\u200f1٬099٫98\xa0US$"

    def test_formatter_rejects_invalid_numbering_system(self, babel_formatter):
        babel_formatter.numbering_system = "xxx"
        with pytest.raises(
            BackendConfigurationError,
            match=r"^Numbering system 'xxx' is not supported",
        ):
            babel_formatter.format(Decimal("2"), "USD", FormatSpec())

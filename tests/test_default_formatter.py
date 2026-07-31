import pytest
from isomoney.formatters import BabelFormatter, FormatSpec
from decimal import Decimal
from isomoney import InvalidFormatSpecError

@pytest.mark.parametrize(
    "compact, accounting, display",
    [
        (True, True, "s"),
        (False, True, "n"),
        (False, True, "h"),
        (True, False, "n"),
    ]
)
def test_babel_format_invalid_format_spec(compact, accounting, display):
    ctx = FormatSpec(compact=compact, accounting=accounting, ccy_display=display)
    fmt = BabelFormatter("USD", "en_US")
    with pytest.raises(InvalidFormatSpecError):
        fmt.format(Decimal(2.99), ctx)


@pytest.mark.parametrize(
        "ccy, expected", [
            ("s", "$2,950,050.299"),
            ("n", "2,950,050.299 US dollars"),
            ("h", "2,950,050.299"),
        ],
        ids= [
            "(standard) - use currency symbol",
            "(standard) - use currency full name",
            "(standard) - hide currency symbol"
        ]
)
def test_default_formatter_standard_format_currency_display(ccy, expected):
    fmt = BabelFormatter("USD", "en_US")
    ctx = FormatSpec(compact=False, accounting=False, ccy_display=ccy)
    result = fmt.format(Decimal("2950050.299"), ctx)
    assert result == expected

@pytest.mark.parametrize(
        "ccy, expected", [
            ("s", "$2,950,050.299"),
            ("h", "2,950,050.299"),
        ],
        ids= [
            "(standard) - use currency symbol",
            "(standard) - hide currency symbol"
        ]
)
def test_default_formatter_compact_format_currency_display(ccy, expected):
    fmt = BabelFormatter("USD", "en_US")
    ctx = FormatSpec(compact=True, accounting=False, ccy_display=ccy)
    result = fmt.format(Decimal("2950050.299"), ctx)
    assert result == expected
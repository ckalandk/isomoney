# pyright: reportGeneralTypeIssues=false
# mypy: ignore-errors
import pytest

from isomoney import Money, formatting
from isomoney.formatting.base_formatter import CcyFormatter
from isomoney.formatting.formatspec import FormatSpec
from isomoney.rounding import RoundingMode


class RecordingFormatter(CcyFormatter):
    def __init__(self):
        super().__init__("")
        self.calls = []

    def format(
        self,
        amount,
        currency,
        ctx,
        *,
        precision,
        rounding,
        omit_trailing_zeros,
    ):
        self.calls.append(
            {
                "amount": amount,
                "currency": currency,
                "ctx": ctx,
                "precision": precision,
                "rounding": rounding,
                "omit_trailing_zeros": omit_trailing_zeros,
            }
        )
        return "dummy"


@pytest.fixture
def formatter():
    formatter = RecordingFormatter()
    formatting.use_backend(formatter)
    return formatter


def test_money_format_forward_amount_and_currency_code(formatter):
    money = Money.from_major(12.34, "USD")
    assert format(money, "") == "dummy"

    assert formatter.calls[0]["amount"] == money.to_decimal()
    assert formatter.calls[0]["currency"] == "USD"


@pytest.mark.parametrize(
    "fmt_spec,expected_ctx",
    [
        pytest.param("hcau", ("hidden", True, True, False)),
        pytest.param("ic", ("iso", True, False, True)),
        pytest.param("nau", ("name", False, True, False)),
    ],
)
def test_money_dunder_format(fmt_spec, expected_ctx):
    formatter = RecordingFormatter()
    formatting.use_backend(formatter)  # type: ignore
    money = Money.from_major(12.34, "USD")

    assert format(money, fmt_spec) == "dummy"

    ctx = formatter.calls[0]["ctx"]
    assert ctx == FormatSpec(*expected_ctx)


def test_money_dunder_format_with_empty_spec_use_formatter_default_format_spec(
    formatter,
):
    money = Money.from_major(12.34, "USD")
    formatter.configure(ccy_display="dummy")  # type: ignore

    assert format(money, "") == "dummy"
    ctx = formatter.calls[0]["ctx"]

    assert ctx.ccy_display == "dummy"


def test_money_format_basic_config(formatter):
    formatting.basicConfig(
        local="xx_XX",
        precision=99,
        rounding=RoundingMode.UNNECESSARY,
        omit_trailing_zeros="False",  # type: ignore
    )
    money = Money.from_major(12.34, "USD")
    assert format(money, "") == "dummy"

    assert formatter.locale == "xx_XX"
    assert formatter.calls[0]["precision"] == 99
    assert formatter.calls[0]["rounding"] == RoundingMode.UNNECESSARY
    assert formatter.calls[0]["omit_trailing_zeros"] == "False"


def test_money_format_with_invalid_format_spec(formatter):
    money = Money.from_major(12.34, "USD")
    with pytest.raises(ValueError) as exc:
        format(money, "x")
    assert "Unknown format code" in str(exc.value)


# Format configuration tests


def test_money_format_use_backend():
    money = Money.from_major(12.34, "USD")
    f1 = RecordingFormatter()
    f2 = RecordingFormatter()

    formatting.use_backend(f1)
    format(money, "")

    formatting.use_backend(f2)
    format(money, "")

    assert len(f1.calls) == 1
    assert len(f2.calls) == 1


def test_money_format_get_formatter(formatter):
    assert formatting.get_formatter() == formatter


def test_money_format_current_backend(formatter):
    assert formatting.current_backend() == formatter.__class__.__name__


def test_money_format_register_backend(monkeypatch):
    registry = {}
    monkeypatch.setattr(formatting._default, "_BACKENDS", registry)

    def factory():
        return RecordingFormatter()

    formatting.register_backend("recording", factory)

    assert registry["recording"] is factory
    assert "recording" in formatting.available_backends()


def test_money_format_register_formatter_class(monkeypatch):
    registry = {}
    monkeypatch.setattr(formatting._default, "_BACKENDS", registry)

    @formatting.register(name="dumb", locale="", bar="bar", foo=42)
    class DumbFormatter(CcyFormatter):
        def __init__(self, locale, bar: str, foo: int):
            super().__init__(locale)
            self.bar = bar
            self.foo = foo

        def format(
            self,
            amount,
            currency,
            ctx,
            *,
            precision,
            rounding,
            omit_trailing_zeros,
        ) -> str:
            return f"dumb(bar={self.bar}, foo={self.foo})"

    assert "dumb" in formatting.available_backends()

    dumbFormatter = registry["dumb"]()
    assert isinstance(dumbFormatter, DumbFormatter)

    formatting.use_backend("dumb")

    money = Money.from_major(12.34, "USD")
    result = formatting.format(money, "")

    assert result == "dumb(bar=bar, foo=42)"


def test_money_format_available_backends():
    assert formatting.available_backends() == ["babel", "icu", "std"]

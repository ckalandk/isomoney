from dataclasses import astuple

import pytest

from pycents import Ccy, Currency


@pytest.fixture
def attributes():
    def make_tuple(ccy):
        return astuple(ccy)

    return make_tuple


def test_currency_new_has_expected_attr(attributes):
    dollar = Currency(Ccy.USD)
    assert attributes(dollar) == Ccy.USD.value


def test_currency_factory_with_str_arg(attributes):
    dollar = Currency.from_code("USD")
    assert attributes(dollar) == Ccy.USD.value


def test_currency_factory_with_ccy_arg(attributes):
    dollar = Currency.from_code(Ccy.USD)
    assert attributes(dollar) == Ccy.USD.value


def test_currency_factory_raises_for_invalid_str_code():
    with pytest.raises(ValueError) as exc_info:
        Currency.from_code("USSD")
    assert str(exc_info.value) == "USSD is not a valid ISO 4217 currency code."


def test_currency_returns_same_instance_for_same_arguments():
    dollar1 = Currency(Ccy.USD)
    dollar2 = Currency(Ccy.USD)
    dollar3 = Currency.from_code("USD")
    assert dollar2 is dollar1
    assert dollar3 is dollar1

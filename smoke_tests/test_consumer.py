from isomoney import Money, formatting


def test_basic_usage():
    money = Money.from_major("1234.56", "USD")

    formatted_money = formatting.format(money, "")
    assert formatted_money == "USD\xa01,234.56"

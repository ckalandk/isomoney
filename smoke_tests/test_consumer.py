from isomoney import Money, formatting


def test_basic_usage():
    # Create a Money object
    money = Money.from_major(1234.56, "USD")

    # Format the Money object using the default formatter
    formatted_money = formatting.format(money, "")

    # Assert that the formatted string is as expected
    assert formatted_money == "1,234.56 USD"

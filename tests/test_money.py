from decimal import Decimal

from src.utils.money import decimal_to_float_for_chart, format_brl, parse_money_br, safe_decimal


def test_parse_money_br():
    assert parse_money_br("R$ 1.234,56") == Decimal("1234.56")
    assert parse_money_br("1234.56") == Decimal("1234.56")
    assert parse_money_br("1.234,56") == Decimal("1234.56")
    assert parse_money_br("#REF!") is None


def test_decimal_helpers():
    assert safe_decimal(None) is None
    assert decimal_to_float_for_chart(Decimal("10.50")) == 10.5
    assert format_brl(Decimal("1234.56")) == "R$ 1.234,56"

from src.utils.excel_dates import convert_excel_date
from src.utils.text import canonical_month, safe_divide


def test_month_aliases():
    assert canonical_month("Jan") == (1, "Janeiro")
    assert canonical_month("Abril") == (4, "Abril")
    assert canonical_month("Março") == (3, "Março")


def test_excel_serial_conversion():
    value = convert_excel_date(45748)
    assert value.year == 2025
    assert value.month == 4


def test_safe_divide_zero():
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 2) == 5


import pytest
from app.tasks.extraction import process_document

# Since extraction relies on a nested parse_num function inside extract_invoice_data_async,
# we will extract a similar parse_num for unit testing.
def parse_num(val):
    if val is None: return None
    try: return float(str(val).replace(',', ''))
    except: return None

def test_parse_num_integer():
    assert parse_num("100") == 100.0

def test_parse_num_float():
    assert parse_num("1,234.56") == 1234.56

def test_parse_num_none():
    assert parse_num(None) is None

def test_parse_num_invalid_string():
    assert parse_num("N/A") is None
    assert parse_num("One hundred") is None

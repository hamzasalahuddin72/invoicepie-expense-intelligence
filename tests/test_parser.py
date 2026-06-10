from parser import parse_invoice_text


def test_parse_standard_invoice_text():
    invoice_text = """
    ABC Hotel Ltd

    Invoice Number: INV-1001
    Invoice Date: 04/06/2026
    Due Date: 18/06/2026
    VAT Number: GB123456789

    Subtotal: £1,000.00
    VAT: £200.00
    Total: £1,200.00

    Payment Status: Unpaid
    Category: Accommodation
    """

    result = parse_invoice_text(invoice_text)

    assert result["supplier_name"] == "ABC Hotel Ltd"
    assert result["invoice_number"] == "INV-1001"
    assert result["invoice_date"] == "2026-06-04"
    assert result["due_date"] == "2026-06-18"
    assert result["vat_number"] == "GB123456789"
    assert result["subtotal"] == 1000.0
    assert result["vat_amount"] == 200.0
    assert result["total_amount"] == 1200.0
    assert result["payment_status"] == "Unpaid"
    assert result["category"] == "Accommodation"


def test_parse_invoice_with_label_variations():
    invoice_text = """
    London Transfer Services

    Invoice No: TR-2201
    Date: 05/06/2026
    Pay By: 20/06/2026
    VAT Registration: GB987654321

    Net Amount: £300.00
    Tax: £60.00
    Amount Due: £360.00

    Status: Unpaid
    Expense Category: Transport
    """

    result = parse_invoice_text(invoice_text)

    assert result["supplier_name"] == "London Transfer Services"
    assert result["invoice_number"] == "TR-2201"
    assert result["invoice_date"] == "2026-06-05"
    assert result["due_date"] == "2026-06-20"
    assert result["vat_number"] == "GB987654321"
    assert result["subtotal"] == 300.0
    assert result["vat_amount"] == 60.0
    assert result["total_amount"] == 360.0
    assert result["payment_status"] == "Unpaid"
    assert result["category"] == "Transport"

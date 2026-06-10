from ai_assisted_extractor import build_ai_extraction_prompt, local_ai_assisted_extract


def test_ai_prompt_contains_required_schema():
    invoice_text = "Example invoice text"
    prompt = build_ai_extraction_prompt(invoice_text)

    assert "supplier_name" in prompt
    assert "invoice_number" in prompt
    assert "total_amount" in prompt
    assert "Return only valid JSON" in prompt


def test_local_ai_assisted_extract_handles_messy_labels():
    messy_text = """
    Brighton Digital Services Ltd

    BILL REF: BDS-9081
    Issued: 09 June 2026
    Please pay before: 24 June 2026
    Company VAT ID: GB777888999

    Before tax: £420.00
    Tax charged: £84.00
    Balance payable: £504.00

    Payment state: Awaiting Payment
    Cost type: Software
    """

    result = local_ai_assisted_extract(messy_text)

    assert result["supplier_name"] == "Brighton Digital Services Ltd"
    assert result["invoice_number"] == "BDS-9081"
    assert result["invoice_date"] == "2026-06-09"
    assert result["due_date"] == "2026-06-24"
    assert result["vat_number"] == "GB777888999"
    assert result["subtotal"] == 420.0
    assert result["vat_amount"] == 84.0
    assert result["total_amount"] == 504.0
    assert result["payment_status"] == "Unpaid"
    assert result["category"] == "Software"

from duplicate_detector import amounts_match, compare_invoice_pair


def test_amounts_match_with_same_values():
    assert amounts_match(1200.0, 1200.0) is True


def test_amounts_do_not_match_with_different_values():
    assert amounts_match(1200.0, 360.0) is False


def test_compare_invoice_pair_finds_likely_duplicate():
    invoice_a = {
        "_record_file": "hotel_invoice_001.json",
        "supplier_name": "ABC Hotel Ltd",
        "invoice_number": "INV-1001",
        "invoice_date": "2026-06-04",
        "due_date": "2026-06-18",
        "total_amount": 1200.0,
        "source_file": "hotel_invoice_001.pdf",
    }

    invoice_b = {
        "_record_file": "hotel_invoice_001_copy.json",
        "supplier_name": "ABC Hotel Ltd",
        "invoice_number": "INV-1001",
        "invoice_date": "2026-06-04",
        "due_date": "2026-06-18",
        "total_amount": 1200.0,
        "source_file": "hotel_invoice_001_copy.pdf",
    }

    match = compare_invoice_pair(invoice_a, invoice_b)

    assert match is not None
    assert match["match_type"] == "likely_duplicate"
    assert match["similarity_score"] == 100


def test_compare_invoice_pair_ignores_different_invoice():
    invoice_a = {
        "_record_file": "hotel_invoice_001.json",
        "supplier_name": "ABC Hotel Ltd",
        "invoice_number": "INV-1001",
        "invoice_date": "2026-06-04",
        "due_date": "2026-06-18",
        "total_amount": 1200.0,
        "source_file": "hotel_invoice_001.pdf",
    }

    invoice_b = {
        "_record_file": "transport_invoice_001.json",
        "supplier_name": "London Transfer Services",
        "invoice_number": "TR-2201",
        "invoice_date": "2026-06-05",
        "due_date": "2026-06-20",
        "total_amount": 360.0,
        "source_file": "transport_invoice_001.pdf",
    }

    match = compare_invoice_pair(invoice_a, invoice_b)

    assert match is None

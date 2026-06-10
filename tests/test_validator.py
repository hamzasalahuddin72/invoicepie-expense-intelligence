from validator import validate_invoice


def test_valid_invoice_passes_validation():
    invoice = {
        "supplier_name": "ABC Hotel Ltd",
        "invoice_number": "INV-1001",
        "invoice_date": "2026-06-04",
        "due_date": "2026-06-18",
        "vat_number": "GB123456789",
        "subtotal": 1000.0,
        "vat_amount": 200.0,
        "total_amount": 1200.0,
        "payment_status": "Unpaid",
        "category": "Accommodation",
        "currency": "GBP",
        "source_file": "hotel_invoice_001.pdf",
    }

    report = validate_invoice(invoice)

    assert report["validation_status"] == "passed"
    assert report["summary"]["total_issues"] == 0
    assert report["issues"] == []


def test_wrong_total_requires_review():
    invoice = {
        "supplier_name": "Bright Advisory Ltd",
        "invoice_number": "CON-4101",
        "invoice_date": "2026-06-07",
        "due_date": "2026-06-22",
        "vat_number": "GB555111222",
        "subtotal": 500.0,
        "vat_amount": 100.0,
        "total_amount": 700.0,
        "payment_status": "Unpaid",
        "category": "Consulting",
        "currency": "GBP",
        "source_file": "consulting_invoice_wrong_total.pdf",
    }

    report = validate_invoice(invoice)

    assert report["validation_status"] == "review_required"
    assert report["summary"]["high_risk_issues"] == 1
    assert any(issue["field"] == "total_amount" for issue in report["issues"])


def test_missing_vat_number_creates_warning():
    invoice = {
        "supplier_name": "TechCloud Software Ltd",
        "invoice_number": "SW-3301",
        "invoice_date": "2026-06-06",
        "due_date": "2026-06-21",
        "vat_number": None,
        "subtotal": 250.0,
        "vat_amount": 50.0,
        "total_amount": 300.0,
        "payment_status": "Pending",
        "category": "Software",
        "currency": "GBP",
        "source_file": "software_invoice_missing_vat.pdf",
    }

    report = validate_invoice(invoice)

    assert report["validation_status"] == "warning"
    assert report["summary"]["medium_risk_issues"] == 1
    assert any(issue["field"] == "vat_number" for issue in report["issues"])


def test_invalid_payment_status_creates_warning():
    invoice = {
        "supplier_name": "Office Supplies Direct",
        "invoice_number": "OFF-7788",
        "invoice_date": "2026-06-08",
        "due_date": "2026-06-23",
        "vat_number": "GB222333444",
        "subtotal": 120.0,
        "vat_amount": 24.0,
        "total_amount": 144.0,
        "payment_status": "Processing",
        "category": "Office Supplies",
        "currency": "GBP",
        "source_file": "office_invoice_invalid_status.pdf",
    }

    report = validate_invoice(invoice)

    assert report["validation_status"] == "warning"
    assert report["summary"]["medium_risk_issues"] == 1
    assert any(issue["field"] == "payment_status" for issue in report["issues"])

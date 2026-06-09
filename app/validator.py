import json
from datetime import date
from pathlib import Path
from typing import Any, Optional


REQUIRED_FIELDS = [
    "supplier_name",
    "invoice_number",
    "invoice_date",
    "due_date",
    "subtotal",
    "vat_amount",
    "total_amount",
    "payment_status",
    "category",
]


VALID_PAYMENT_STATUSES = {"paid", "unpaid", "pending", "overdue"}


def load_invoice_json(json_path: str) -> dict:
    """
    Load parsed invoice data from a JSON file.
    """
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"Invoice JSON not found: {json_path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    """
    Convert an ISO date string into a date object.
    """
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def add_issue(issues: list, field: str, severity: str, message: str) -> None:
    """
    Add a validation issue to the report.
    """
    issues.append(
        {
            "field": field,
            "severity": severity,
            "message": message,
        }
    )


def validate_required_fields(invoice_data: dict, issues: list) -> None:
    """
    Check that required invoice fields are present.
    """
    for field in REQUIRED_FIELDS:
        value = invoice_data.get(field)

        if value is None or value == "":
            add_issue(
                issues,
                field,
                "high",
                f"Required field '{field}' is missing.",
            )


def validate_dates(invoice_data: dict, issues: list) -> None:
    """
    Validate invoice and due dates.
    """
    invoice_date = parse_iso_date(invoice_data.get("invoice_date"))
    due_date = parse_iso_date(invoice_data.get("due_date"))

    if invoice_data.get("invoice_date") and invoice_date is None:
        add_issue(
            issues,
            "invoice_date",
            "high",
            "Invoice date is not in a valid ISO date format.",
        )

    if invoice_data.get("due_date") and due_date is None:
        add_issue(
            issues,
            "due_date",
            "high",
            "Due date is not in a valid ISO date format.",
        )

    if invoice_date and due_date and due_date < invoice_date:
        add_issue(
            issues,
            "due_date",
            "high",
            "Due date is earlier than the invoice date.",
        )


def is_valid_amount(value: Any) -> bool:
    """
    Check whether a value is a valid non-negative number.
    """
    return isinstance(value, (int, float)) and value >= 0


def validate_amounts(invoice_data: dict, issues: list) -> None:
    """
    Validate subtotal, VAT and total amount fields.
    """
    subtotal = invoice_data.get("subtotal")
    vat_amount = invoice_data.get("vat_amount")
    total_amount = invoice_data.get("total_amount")

    for field in ["subtotal", "vat_amount", "total_amount"]:
        value = invoice_data.get(field)

        if value is not None and not is_valid_amount(value):
            add_issue(
                issues,
                field,
                "high",
                f"Field '{field}' must be a valid non-negative number.",
            )

    if (
        is_valid_amount(subtotal)
        and is_valid_amount(vat_amount)
        and is_valid_amount(total_amount)
    ):
        expected_total = round(subtotal + vat_amount, 2)
        actual_total = round(total_amount, 2)

        if abs(expected_total - actual_total) > 0.01:
            add_issue(
                issues,
                "total_amount",
                "high",
                f"Subtotal plus VAT should equal total. Expected {expected_total}, found {actual_total}.",
            )


def validate_payment_status(invoice_data: dict, issues: list) -> None:
    """
    Validate payment status value.
    """
    payment_status = invoice_data.get("payment_status")

    if payment_status:
        normalised_status = str(payment_status).strip().lower()

        if normalised_status not in VALID_PAYMENT_STATUSES:
            add_issue(
                issues,
                "payment_status",
                "medium",
                f"Payment status '{payment_status}' is not one of the expected values: paid, unpaid, pending, overdue.",
            )


def validate_invoice(invoice_data: dict) -> dict:
    """
    Run all validation checks and return a structured validation report.
    """
    issues = []

    validate_required_fields(invoice_data, issues)
    validate_dates(invoice_data, issues)
    validate_amounts(invoice_data, issues)
    validate_payment_status(invoice_data, issues)

    high_risk_count = sum(1 for issue in issues if issue["severity"] == "high")
    medium_risk_count = sum(1 for issue in issues if issue["severity"] == "medium")

    if high_risk_count > 0:
        status = "review_required"
    elif medium_risk_count > 0:
        status = "warning"
    else:
        status = "passed"

    return {
        "source_file": invoice_data.get("source_file"),
        "invoice_number": invoice_data.get("invoice_number"),
        "supplier_name": invoice_data.get("supplier_name"),
        "validation_status": status,
        "summary": {
            "total_issues": len(issues),
            "high_risk_issues": high_risk_count,
            "medium_risk_issues": medium_risk_count,
        },
        "issues": issues,
    }


def save_validation_report(report: dict, output_path: str) -> None:
    """
    Save the validation report to a JSON file.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    input_json = "data/extracted_json/hotel_invoice_001.json"
    output_json = "data/validation_reports/hotel_invoice_001_validation.json"

    invoice = load_invoice_json(input_json)
    validation_report = validate_invoice(invoice)
    save_validation_report(validation_report, output_json)

    print(json.dumps(validation_report, indent=4, ensure_ascii=False))
    print(f"\nValidation report saved to: {output_json}")

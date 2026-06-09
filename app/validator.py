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

    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    """
    Convert an ISO date string into a Python date object.
    """
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def add_issue(issues: list, field: str, severity: str, message: str) -> None:
    """
    Add a structured validation issue to the report.
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
    Check that important invoice fields are present.
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
    Check invoice date and due date values.
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
    Check subtotal, VAT and total amount fields.
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


def validate_vat_fields(invoice_data: dict, issues: list) -> None:
    """
    Flag cases where VAT is charged but no VAT number is present.
    """
    vat_amount = invoice_data.get("vat_amount")
    vat_number = invoice_data.get("vat_number")

    if is_valid_amount(vat_amount) and vat_amount > 0 and not vat_number:
        add_issue(
            issues,
            "vat_number",
            "medium",
            "VAT amount is present but VAT number is missing.",
        )


def validate_payment_status(invoice_data: dict, issues: list) -> None:
    """
    Check whether payment status is one of the expected values.
    """
    payment_status = invoice_data.get("payment_status")

    if payment_status:
        normalised_status = str(payment_status).strip().lower()

        if normalised_status not in VALID_PAYMENT_STATUSES:
            add_issue(
                issues,
                "payment_status",
                "medium",
                f"Payment status '{payment_status}' is not one of: paid, unpaid, pending, overdue.",
            )


def validate_invoice(invoice_data: dict) -> dict:
    """
    Run all invoice validation checks and return a structured report.
    """
    issues = []

    validate_required_fields(invoice_data, issues)
    validate_dates(invoice_data, issues)
    validate_amounts(invoice_data, issues)
    validate_vat_fields(invoice_data, issues)
    validate_payment_status(invoice_data, issues)

    high_risk_count = sum(1 for issue in issues if issue["severity"] == "high")
    medium_risk_count = sum(1 for issue in issues if issue["severity"] == "medium")

    if high_risk_count > 0:
        validation_status = "review_required"
    elif medium_risk_count > 0:
        validation_status = "warning"
    else:
        validation_status = "passed"

    return {
        "source_file": invoice_data.get("source_file"),
        "invoice_number": invoice_data.get("invoice_number"),
        "supplier_name": invoice_data.get("supplier_name"),
        "validation_status": validation_status,
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


def clear_existing_validation_reports(output_folder: str) -> None:
    """
    Remove old validation report JSON files before a fresh batch run.
    """
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)

    for json_file in folder.glob("*.json"):
        json_file.unlink()


def validate_invoice_folder(input_folder: str, output_folder: str) -> int:
    """
    Validate all parsed invoice JSON files in a folder.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    if not input_path.exists():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    clear_existing_validation_reports(output_folder)

    count = 0

    for json_file in sorted(input_path.glob("*.json")):
        invoice = load_invoice_json(str(json_file))
        validation_report = validate_invoice(invoice)

        output_json = output_path / f"{json_file.stem}_validation.json"
        save_validation_report(validation_report, str(output_json))

        count += 1
        print(
            f"Validated {json_file.name} -> {output_json} "
            f"({validation_report['validation_status']})"
        )

    return count


if __name__ == "__main__":
    input_folder = "data/extracted_json"
    output_folder = "data/validation_reports"

    validated_count = validate_invoice_folder(input_folder, output_folder)

    print(f"\nValidated {validated_count} invoice JSON files.")

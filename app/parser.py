import json
import re
from pathlib import Path
from typing import Optional

from dateutil import parser as date_parser
from extractor import extract_text_from_pdf


FIELD_LABELS = {
    "invoice_number": ["Invoice Number", "Invoice No", "Invoice ID", "Ref No", "Reference"],
    "invoice_date": ["Invoice Date", "Date"],
    "due_date": ["Due Date", "Payment Due", "Pay By"],
    "vat_number": ["VAT Number", "VAT Registration", "VAT Reg No"],
    "subtotal": ["Subtotal", "Net Amount", "Net Total"],
    "vat_amount": ["VAT Amount", "VAT", "Tax", "Tax Amount"],
    "total_amount": ["Total Amount", "Grand Total", "Amount Due", "Balance Due", "Total"],
    "payment_status": ["Payment Status", "Status"],
    "category": ["Expense Category", "Category"],
}


def find_label_value(text: str, labels: list[str]) -> Optional[str]:
    """
    Find a value from labelled invoice lines.

    Example:
    Invoice Number: INV-1001
    Amount Due: £1,200.00
    """
    for label in labels:
        pattern = rf"^\s*{re.escape(label)}\s*:\s*(.+?)\s*$"
        match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None


def clean_amount(value: Optional[str]) -> Optional[float]:
    """
    Convert amount strings like £1,200.00 into 1200.00.
    """
    if not value:
        return None

    cleaned = (
        value.replace("£", "")
        .replace("\u00a3", "")
        .replace(",", "")
        .replace("GBP", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


def clean_date(value: Optional[str]) -> Optional[str]:
    """
    Convert common UK date formats into ISO format: YYYY-MM-DD.
    """
    if not value:
        return None

    try:
        return date_parser.parse(value, dayfirst=True).date().isoformat()
    except (ValueError, TypeError):
        return None


def find_supplier_name(text: str) -> Optional[str]:
    """
    Use the first meaningful non-empty line as the supplier name.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    ignored_prefixes = (
        "--- Page",
        "Invoice Number",
        "Invoice No",
        "Invoice ID",
        "Ref No",
        "Reference",
        "Invoice Date",
        "Date",
        "Due Date",
        "Payment Due",
        "Pay By",
        "VAT Number",
        "VAT Registration",
        "VAT Reg No",
        "Subtotal",
        "Net Amount",
        "Net Total",
        "VAT Amount",
        "VAT:",
        "Tax",
        "Tax Amount",
        "Total Amount",
        "Grand Total",
        "Amount Due",
        "Balance Due",
        "Total",
        "Payment Status",
        "Status",
        "Expense Category",
        "Category",
    )

    for line in lines:
        if not line.startswith(ignored_prefixes):
            return line

    return None


def parse_invoice_text(text: str) -> dict:
    """
    Convert extracted invoice text into structured invoice data.
    """
    invoice_data = {
        "supplier_name": find_supplier_name(text),
        "invoice_number": find_label_value(text, FIELD_LABELS["invoice_number"]),
        "invoice_date": clean_date(find_label_value(text, FIELD_LABELS["invoice_date"])),
        "due_date": clean_date(find_label_value(text, FIELD_LABELS["due_date"])),
        "vat_number": find_label_value(text, FIELD_LABELS["vat_number"]),
        "subtotal": clean_amount(find_label_value(text, FIELD_LABELS["subtotal"])),
        "vat_amount": clean_amount(find_label_value(text, FIELD_LABELS["vat_amount"])),
        "total_amount": clean_amount(find_label_value(text, FIELD_LABELS["total_amount"])),
        "payment_status": find_label_value(text, FIELD_LABELS["payment_status"]),
        "category": find_label_value(text, FIELD_LABELS["category"]),
        "currency": "GBP",
    }

    return invoice_data


def parse_invoice_pdf(pdf_path: str) -> dict:
    """
    Extract text from a PDF invoice, then parse it into structured JSON-ready data.
    """
    text = extract_text_from_pdf(pdf_path)
    invoice_data = parse_invoice_text(text)
    invoice_data["source_file"] = Path(pdf_path).name

    return invoice_data


def save_invoice_json(invoice_data: dict, output_path: str) -> None:
    """
    Save parsed invoice data to a JSON file.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(invoice_data, file, indent=4, ensure_ascii=False)


def clear_existing_json_outputs(output_folder: str) -> None:
    """
    Remove old extracted JSON files before a fresh batch parse.
    """
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)

    for json_file in folder.glob("*.json"):
        json_file.unlink()


def parse_invoice_folder(input_folder: str, output_folder: str) -> int:
    """
    Parse all PDF invoices in a folder and save one JSON file per invoice.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    if not input_path.exists():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    clear_existing_json_outputs(output_folder)

    count = 0

    for pdf_file in sorted(input_path.glob("*.pdf")):
        parsed_invoice = parse_invoice_pdf(str(pdf_file))
        output_json = output_path / f"{pdf_file.stem}.json"
        save_invoice_json(parsed_invoice, str(output_json))
        count += 1
        print(f"Parsed {pdf_file.name} -> {output_json}")

    return count


if __name__ == "__main__":
    input_folder = "data/sample_invoices"
    output_folder = "data/extracted_json"

    parsed_count = parse_invoice_folder(input_folder, output_folder)

    print(f"\nParsed {parsed_count} invoice PDF files.")

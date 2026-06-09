import json
import re
from pathlib import Path
from typing import Optional
from dateutil import parser as date_parser

from extractor import extract_text_from_pdf


def find_label_value(text: str, label: str) -> Optional[str]:
    """
    Find values from lines like:
    Invoice Number: INV-1001
    Total: £1,200.00
    """
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
        "Invoice Date",
        "Due Date",
        "VAT Number",
        "Subtotal",
        "VAT:",
        "Total",
        "Payment Status",
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
        "invoice_number": find_label_value(text, "Invoice Number"),
        "invoice_date": clean_date(find_label_value(text, "Invoice Date")),
        "due_date": clean_date(find_label_value(text, "Due Date")),
        "vat_number": find_label_value(text, "VAT Number"),
        "subtotal": clean_amount(find_label_value(text, "Subtotal")),
        "vat_amount": clean_amount(find_label_value(text, "VAT")),
        "total_amount": clean_amount(find_label_value(text, "Total")),
        "payment_status": find_label_value(text, "Payment Status"),
        "category": find_label_value(text, "Category"),
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


if __name__ == "__main__":
    sample_pdf = "data/sample_invoices/hotel_invoice_001.pdf"
    output_json = "data/extracted_json/hotel_invoice_001.json"

    parsed_invoice = parse_invoice_pdf(sample_pdf)
    save_invoice_json(parsed_invoice, output_json)

    print(json.dumps(parsed_invoice, indent=4, ensure_ascii=False))
    print(f"\nStructured invoice JSON saved to: {output_json}")

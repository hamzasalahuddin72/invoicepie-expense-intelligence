import json
import re
from pathlib import Path
from typing import Optional

from dateutil import parser as date_parser


AI_OUTPUT_FOLDER = Path("data/ai_extracted_json")


def read_text_file(file_path: str) -> str:
    """
    Read messy invoice text from a local text file.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")

    return path.read_text(encoding="utf-8-sig")


def build_ai_extraction_prompt(invoice_text: str) -> str:
    """
    Build a structured extraction prompt for a future LLM-based extraction step.

    This function does not call an AI API. It prepares a clear prompt that can later
    be sent to an LLM provider when API integration is added.
    """
    return f"""
You are extracting structured invoice data from messy invoice text.

Return only valid JSON using this exact schema:

{{
  "supplier_name": "",
  "invoice_number": "",
  "invoice_date": "",
  "due_date": "",
  "vat_number": "",
  "subtotal": null,
  "vat_amount": null,
  "total_amount": null,
  "payment_status": "",
  "category": "",
  "currency": "GBP"
}}

Rules:
- Use ISO date format: YYYY-MM-DD.
- Amounts must be numbers, not strings.
- If a field is missing, use null.
- Do not include explanations outside JSON.

Invoice text:
---
{invoice_text}
---
""".strip()


def find_value_after_label(text: str, labels: list[str]) -> Optional[str]:
    """
    Find values from messy invoice text where labels may vary.
    """
    for label in labels:
        pattern = rf"^\s*{re.escape(label)}\s*:\s*(.+?)\s*$"
        match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None


def clean_amount(value: Optional[str]) -> Optional[float]:
    """
    Convert amount strings like £504.00 into 504.0.
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
    Convert common date strings into ISO format.
    """
    if not value:
        return None

    try:
        return date_parser.parse(value, dayfirst=True).date().isoformat()
    except (ValueError, TypeError):
        return None


def normalise_payment_status(value: Optional[str]) -> Optional[str]:
    """
    Convert messy payment wording into the expected InvoicePie status values.
    """
    if not value:
        return None

    value_lower = value.strip().lower()

    if value_lower in {"awaiting payment", "not paid", "unpaid"}:
        return "Unpaid"

    if value_lower in {"paid", "settled"}:
        return "Paid"

    if value_lower in {"pending", "in progress"}:
        return "Pending"

    if value_lower in {"overdue", "late"}:
        return "Overdue"

    return value.strip()


def infer_supplier_name(text: str) -> Optional[str]:
    """
    Infer supplier name from the first meaningful line.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    ignored_starts = (
        "bill ref",
        "issued",
        "please pay",
        "services supplied",
        "company vat",
        "before tax",
        "tax charged",
        "balance payable",
        "payment state",
        "cost type",
    )

    for line in lines:
        if not line.lower().startswith(ignored_starts):
            return line

    return None


def local_ai_assisted_extract(invoice_text: str) -> dict:
    """
    Local AI-assisted extraction prototype.

    This is not a live LLM call. It simulates an AI-assisted extraction layer by
    handling messy label variations and normalising the output into the InvoicePie
    JSON schema. A future milestone can replace or extend this with a real LLM API.
    """
    invoice_data = {
        "supplier_name": infer_supplier_name(invoice_text),
        "invoice_number": find_value_after_label(
            invoice_text,
            ["BILL REF", "Bill Reference", "Reference", "Invoice Ref", "Invoice Number"],
        ),
        "invoice_date": clean_date(
            find_value_after_label(invoice_text, ["Issued", "Issue Date", "Invoice Date", "Date"])
        ),
        "due_date": clean_date(
            find_value_after_label(invoice_text, ["Please pay before", "Pay before", "Due Date", "Payment Due"])
        ),
        "vat_number": find_value_after_label(
            invoice_text,
            ["Company VAT ID", "VAT ID", "VAT Number", "VAT Registration"],
        ),
        "subtotal": clean_amount(
            find_value_after_label(invoice_text, ["Before tax", "Net Amount", "Subtotal"])
        ),
        "vat_amount": clean_amount(
            find_value_after_label(invoice_text, ["Tax charged", "VAT", "VAT Amount", "Tax"])
        ),
        "total_amount": clean_amount(
            find_value_after_label(invoice_text, ["Balance payable", "Amount Due", "Grand Total", "Total"])
        ),
        "payment_status": normalise_payment_status(
            find_value_after_label(invoice_text, ["Payment state", "Payment Status", "Status"])
        ),
        "category": find_value_after_label(invoice_text, ["Cost type", "Expense Category", "Category"]),
        "currency": "GBP",
    }

    return invoice_data


def save_json(data: dict, output_path: str) -> None:
    """
    Save extracted invoice data to JSON.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    input_file = "data/messy_inputs/messy_invoice_001.txt"
    output_json = "data/ai_extracted_json/messy_invoice_001_ai.json"

    messy_text = read_text_file(input_file)

    prompt = build_ai_extraction_prompt(messy_text)
    extracted_data = local_ai_assisted_extract(messy_text)
    extracted_data["source_file"] = Path(input_file).name
    extracted_data["extraction_method"] = "local_ai_assisted_prototype"

    save_json(extracted_data, output_json)

    print("AI extraction prompt prepared:\n")
    print(prompt)

    print("\nLocal AI-assisted extraction output:\n")
    print(json.dumps(extracted_data, indent=4, ensure_ascii=False))

    print(f"\nAI-assisted extraction JSON saved to: {output_json}")

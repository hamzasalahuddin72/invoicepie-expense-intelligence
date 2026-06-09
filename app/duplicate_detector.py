import json
import re
from itertools import combinations
from pathlib import Path
from typing import Any, Optional


def normalise_text(value: Optional[str]) -> str:
    """
    Standardise text values before comparison.
    """
    if not value:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def amounts_match(amount_a: Any, amount_b: Any, tolerance: float = 0.01) -> bool:
    """
    Compare two amount values with a small tolerance for rounding differences.
    """
    try:
        return abs(float(amount_a) - float(amount_b)) <= tolerance
    except (TypeError, ValueError):
        return False


def load_invoice_records(folder_path: str) -> list[dict]:
    """
    Load parsed invoice JSON records from a folder.
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    records = []

    for json_file in sorted(folder.glob("*.json")):
        with open(json_file, "r", encoding="utf-8-sig") as file:
            record = json.load(file)

        record["_record_file"] = json_file.name
        records.append(record)

    return records


def compare_invoice_pair(invoice_a: dict, invoice_b: dict) -> Optional[dict]:
    """
    Compare two invoices and return a duplicate match if the similarity is high enough.
    """
    score = 0
    reasons = []

    supplier_a = normalise_text(invoice_a.get("supplier_name"))
    supplier_b = normalise_text(invoice_b.get("supplier_name"))

    invoice_number_a = normalise_text(invoice_a.get("invoice_number"))
    invoice_number_b = normalise_text(invoice_b.get("invoice_number"))

    invoice_date_a = invoice_a.get("invoice_date")
    invoice_date_b = invoice_b.get("invoice_date")

    due_date_a = invoice_a.get("due_date")
    due_date_b = invoice_b.get("due_date")

    total_a = invoice_a.get("total_amount")
    total_b = invoice_b.get("total_amount")

    if supplier_a and supplier_a == supplier_b:
        score += 25
        reasons.append("Supplier name matches.")

    if invoice_number_a and invoice_number_a == invoice_number_b:
        score += 45
        reasons.append("Invoice number matches.")

    if amounts_match(total_a, total_b):
        score += 20
        reasons.append("Total amount matches.")

    if invoice_date_a and invoice_date_a == invoice_date_b:
        score += 5
        reasons.append("Invoice date matches.")

    if due_date_a and due_date_a == due_date_b:
        score += 5
        reasons.append("Due date matches.")

    if score >= 85:
        match_type = "likely_duplicate"
    elif score >= 60:
        match_type = "possible_duplicate"
    else:
        return None

    return {
        "match_type": match_type,
        "similarity_score": score,
        "reasons": reasons,
        "record_a": {
            "record_file": invoice_a.get("_record_file"),
            "supplier_name": invoice_a.get("supplier_name"),
            "invoice_number": invoice_a.get("invoice_number"),
            "invoice_date": invoice_a.get("invoice_date"),
            "total_amount": invoice_a.get("total_amount"),
            "source_file": invoice_a.get("source_file"),
        },
        "record_b": {
            "record_file": invoice_b.get("_record_file"),
            "supplier_name": invoice_b.get("supplier_name"),
            "invoice_number": invoice_b.get("invoice_number"),
            "invoice_date": invoice_b.get("invoice_date"),
            "total_amount": invoice_b.get("total_amount"),
            "source_file": invoice_b.get("source_file"),
        },
    }


def detect_duplicates(invoice_records: list[dict]) -> dict:
    """
    Compare invoice records and return a duplicate detection report.
    """
    matches = []

    for invoice_a, invoice_b in combinations(invoice_records, 2):
        match = compare_invoice_pair(invoice_a, invoice_b)

        if match:
            matches.append(match)

    return {
        "record_count": len(invoice_records),
        "match_count": len(matches),
        "matches": matches,
    }


def save_duplicate_report(report: dict, output_path: str) -> None:
    """
    Save duplicate detection results to JSON.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8-sig") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    input_folder = "data/extracted_json"
    output_json = "data/duplicate_reports/duplicate_report.json"

    records = load_invoice_records(input_folder)
    duplicate_report = detect_duplicates(records)
    save_duplicate_report(duplicate_report, output_json)

    print(json.dumps(duplicate_report, indent=4, ensure_ascii=False))
    print(f"\nDuplicate report saved to: {output_json}")

# -*- coding: utf-8 -*-

import fitz
from pathlib import Path


OUTPUT_DIR = Path("data/sample_invoices")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


SAMPLE_INVOICES = {
    "hotel_invoice_001.pdf": """
ABC Hotel Ltd

Invoice Number: INV-1001
Invoice Date: 04/06/2026
Due Date: 18/06/2026
VAT Number: GB123456789

Subtotal: \u00a31,000.00
VAT: \u00a3200.00
Total: \u00a31,200.00

Payment Status: Unpaid
Category: Accommodation
""",
    "hotel_invoice_001_copy.pdf": """
ABC Hotel Ltd

Invoice Number: INV-1001
Invoice Date: 04/06/2026
Due Date: 18/06/2026
VAT Number: GB123456789

Subtotal: \u00a31,000.00
VAT: \u00a3200.00
Total: \u00a31,200.00

Payment Status: Unpaid
Category: Accommodation
""",
    "transport_invoice_001.pdf": """
London Transfer Services

Invoice No: TR-2201
Date: 05/06/2026
Pay By: 20/06/2026
VAT Registration: GB987654321

Net Amount: \u00a3300.00
Tax: \u00a360.00
Amount Due: \u00a3360.00

Status: Unpaid
Expense Category: Transport
""",
    "software_invoice_missing_vat.pdf": """
TechCloud Software Ltd

Invoice ID: SW-3301
Invoice Date: 06/06/2026
Due Date: 21/06/2026

Subtotal: \u00a3250.00
VAT: \u00a350.00
Total: \u00a3300.00

Payment Status: Pending
Category: Software
""",
    "consulting_invoice_wrong_total.pdf": """
Bright Advisory Ltd

Invoice Number: CON-4101
Invoice Date: 07/06/2026
Due Date: 22/06/2026
VAT Number: GB555111222

Subtotal: \u00a3500.00
VAT: \u00a3100.00
Total: \u00a3700.00

Payment Status: Unpaid
Category: Consulting
""",
    "office_invoice_invalid_status.pdf": """
Office Supplies Direct

Ref No: OFF-7788
Invoice Date: 08/06/2026
Payment Due: 23/06/2026
VAT Number: GB222333444

Subtotal: \u00a3120.00
VAT Amount: \u00a324.00
Grand Total: \u00a3144.00

Status: Processing
Category: Office Supplies
""",
}


def create_invoice_pdf(file_name: str, invoice_text: str) -> None:
    output_path = OUTPUT_DIR / file_name

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), invoice_text.strip(), fontsize=11)
    doc.save(output_path)
    doc.close()

    print(f"Created sample invoice: {output_path}")


def main() -> None:
    for file_name, invoice_text in SAMPLE_INVOICES.items():
        create_invoice_pdf(file_name, invoice_text)

    print(f"\nCreated {len(SAMPLE_INVOICES)} sample invoice PDFs.")


if __name__ == "__main__":
    main()

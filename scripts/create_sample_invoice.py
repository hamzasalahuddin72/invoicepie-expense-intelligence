# -*- coding: utf-8 -*-

import fitz
from pathlib import Path

output_dir = Path("data/sample_invoices")
output_dir.mkdir(parents=True, exist_ok=True)

invoice_text = """
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
"""

doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), invoice_text, fontsize=11)
doc.save("data/sample_invoices/hotel_invoice_001.pdf")
doc.close()

print("Sample invoice created: data/sample_invoices/hotel_invoice_001.pdf")

# InvoicePie Project Log

## Project Name
InvoicePie

## Repository
invoicepie-expense-intelligence

## Project Purpose
InvoicePie is an AI-powered invoice and expense intelligence system designed to extract structured data from invoice PDFs, validate missing or suspicious fields, detect duplicates, and produce business expense insights.

---

## Milestone 1 — Project Setup and First Sample Invoice

### Completed Steps

- Created local project folder: `invoicepie-expense-intelligence`.
- Initialised local Git repository for InvoicePie.
- Created initial project structure with `app`, `data`, `tests`, `README.md`, `requirements.txt`, and `.gitignore`.
- Added initial Python dependencies in `requirements.txt`.
- Created and activated a Python virtual environment.
- Installed project dependencies from `requirements.txt`.
- Created a script folder for utility scripts.
- Created `scripts/create_sample_invoice.py` to generate a fake invoice PDF for testing.
- Fixed Windows encoding issue caused by the pound symbol in the generated invoice text.
- Successfully created the first fake sample invoice PDF: `data/sample_invoices/hotel_invoice_001.pdf`.

### Current Status

The project has a clean starting structure, working Python environment, installed dependencies, and one generated fake invoice PDF ready for testing PDF text extraction.

### Latest Completed Progress Line

Completed: Fixed Windows encoding issue and created the first fake sample invoice PDF.

---

## Next Step

Implement the first PDF text extraction script using PyMuPDF in `app/extractor.py`, then test whether the sample invoice text can be printed in the terminal.

## Milestone 2 — PDF Text Extraction

### Completed Steps

- Implemented `app/extractor.py` using PyMuPDF.
- Added a reusable `extract_text_from_pdf()` function.
- Tested the extractor with `data/sample_invoices/hotel_invoice_001.pdf`.
- Confirmed that invoice text can be extracted and printed in the terminal.

### Why This Matters

This is the first working document-processing step in InvoicePie. The system can now read text-based invoice PDFs, which creates the foundation for parsing invoice fields, validating invoice data, detecting duplicates, and producing expense insights later.

### Latest Completed Progress Line

Completed: Implemented and tested PDF text extraction from the first sample invoice.

### Next Step

Build `app/parser.py` to convert extracted invoice text into structured JSON fields such as supplier name, invoice number, invoice date, due date, VAT number, subtotal, VAT amount, total amount, payment status, and category.

## Milestone 3 — Structured Invoice Parsing

### Completed Steps

- Implemented `app/parser.py` to convert extracted invoice text into structured invoice data.
- Added helper functions to identify labelled invoice fields such as invoice number, dates, VAT number, subtotal, VAT amount, total amount, payment status, and category.
- Added basic cleaning for UK currency amounts and date formatting.
- Parsed the first sample invoice into a JSON-ready Python dictionary.
- Saved the structured invoice output to `data/extracted_json/hotel_invoice_001.json`.

### Why This Matters

InvoicePie can now move beyond raw PDF text extraction. The project has its first working data pipeline: a PDF invoice can be read, key business fields can be extracted, and the result can be stored as structured JSON. This creates the foundation for validation rules, duplicate detection, database storage, and dashboard insights.

### Next Step

Build `app/validator.py` to check whether important invoice fields are missing, whether amounts are valid, and whether the invoice looks ready for business processing.

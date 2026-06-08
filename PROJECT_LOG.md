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

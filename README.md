<table>
  <tr>
    <td width="150">
      <img src="docs/assets/invoicepie-app-icon.png" alt="InvoicePie app icon" width="110"/>
    </td>
    <td>
      <h1>InvoicePie — AI-Powered Invoice and Expense Intelligence</h1>
    </td>
  </tr>
</table>

AI-powered invoice and expense intelligence system for extracting structured data from invoice PDFs, validating missing or suspicious fields, detecting duplicate invoices, and presenting expense insights.

[![InvoicePie Live Demo](docs/assets/invoicepie-live-badge.svg)](https://invoicepie.streamlit.app/)

**Live Demo:** https://invoicepie.streamlit.app/

InvoicePie is an AI-powered invoice and expense intelligence system that extracts structured data from invoice PDFs, validates missing or suspicious fields, detects duplicate invoices, stores processed records in a database, and presents expense insights through a dashboard.

This project is being built as a practical portfolio project to demonstrate applied AI engineering, document processing, Python development, database design, validation logic, duplicate detection, and dashboard reporting.

---

## Current Status

InvoicePie currently supports a working local pipeline:

```text
Sample invoice PDF
↓
PDF text extraction
↓
Invoice field parsing
↓
Structured JSON output
↓
Invoice validation report
↓
Duplicate detection report
↓
SQLite database storage
↓
Streamlit expense dashboard
```

The current sample dataset includes:

```text
3 invoice records
1 validation report
1 duplicate invoice match
```

The dashboard currently shows:

```text
Invoices: 3
Total Spend: £2,760.00
Unpaid Invoices: 3
Validation Issues: 0
Duplicate Matches: 1
```

---

## Features Implemented

### PDF Text Extraction

InvoicePie can extract readable text from a text-based invoice PDF using PyMuPDF.

Current file:

```text
app/extractor.py
```

### Structured Invoice Parsing

Extracted invoice text is converted into structured JSON fields such as:

```text
supplier_name
invoice_number
invoice_date
due_date
vat_number
subtotal
vat_amount
total_amount
payment_status
category
currency
source_file
```

Current file:

```text
app/parser.py
```

### Invoice Validation

Parsed invoice records are checked for missing or suspicious values.

Current validation checks include:

```text
required fields are present
invoice date is valid
due date is valid
due date is not earlier than invoice date
subtotal is valid
VAT amount is valid
total amount is valid
subtotal plus VAT matches total amount
payment status uses an expected value
```

Current file:

```text
app/validator.py
```

### Duplicate Invoice Detection

InvoicePie compares parsed invoice records and flags likely duplicates using:

```text
supplier name
invoice number
invoice date
due date
total amount
```

Current file:

```text
app/duplicate_detector.py
```

### SQLite Database Storage

Processed invoice records, validation reports and duplicate matches are stored in a local SQLite database.

Current file:

```text
app/database.py
```

Database tables:

```text
invoices
validation_reports
duplicate_matches
```

### Streamlit Dashboard

A local Streamlit dashboard displays summary metrics, spend insights, invoice records, validation results and duplicate warnings.

Current file:

```text
app/dashboard.py
```

---

## Tech Stack

```text
Python
PyMuPDF
pandas
SQLite
Streamlit
python-dateutil
Git / GitHub
```

Planned later additions may include:

```text
OCR support
PostgreSQL
FastAPI
Docker
cloud deployment
AI-assisted invoice review
```

---

## Project Structure

```text
invoicepie-expense-intelligence/
│
├── app/
│   ├── dashboard.py
│   ├── database.py
│   ├── duplicate_detector.py
│   ├── extractor.py
│   ├── main.py
│   ├── parser.py
│   └── validator.py
│
├── data/
│   ├── database/
│   ├── duplicate_reports/
│   ├── extracted_json/
│   ├── sample_invoices/
│   └── validation_reports/
│
├── docs/
│   └── screenshots/
│
├── scripts/
│   └── create_sample_invoice.py
│
├── tests/
├── PROJECT_LOG.md
├── README.md
├── requirements.txt
└── .gitignore
```

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/hamzasalahuddin72/invoicepie-expense-intelligence.git
cd invoicepie-expense-intelligence
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Generate the sample invoice PDF

```powershell
python scripts/create_sample_invoice.py
```

This creates:

```text
data/sample_invoices/hotel_invoice_001.pdf
```

### 5. Extract text from the sample invoice

```powershell
python app/extractor.py
```

### 6. Parse the invoice into structured JSON

```powershell
python app/parser.py
```

This creates:

```text
data/extracted_json/hotel_invoice_001.json
```

### 7. Run invoice validation

```powershell
python app/validator.py
```

This creates:

```text
data/validation_reports/hotel_invoice_001_validation.json
```

### 8. Run duplicate detection

```powershell
python app/duplicate_detector.py
```

This creates:

```text
data/duplicate_reports/duplicate_report.json
```

### 9. Import processed data into SQLite

```powershell
python app/database.py
```

This creates the local database:

```text
data/database/invoicepie.db
```

### 10. Launch the dashboard

```powershell
python -m streamlit run app/dashboard.py
```

Then open:

```text
http://localhost:8501
```

---

## Example Output

The current dashboard displays:

```text
Invoices: 3
Total Spend: £2,760.00
Unpaid Invoices: 3
Validation Issues: 0
Duplicate Matches: 1
```

The duplicate detector currently identifies one likely duplicate between:

```text
hotel_invoice_001.json
hotel_invoice_001_duplicate.json
```

---

## Current Limitations

InvoicePie is currently an MVP and works with a small sample dataset.

Current limitations:

```text
only text-based PDF invoices are supported
scanned invoices are not supported yet
the parser depends on predictable invoice labels
duplicate detection uses rule-based scoring
the SQLite database is local only
the dashboard is not deployed online yet
there is no file upload interface yet
there is no authentication or user management
```

These limitations are intentional at this stage. The project is being built milestone by milestone so each part of the system can be understood, tested and improved.

---

## Planned Improvements

Planned next steps include:

```text
add more varied sample invoices
add bad invoice examples for validation testing
improve duplicate detection for near-matches
add dashboard filters
add file upload from the dashboard
add export options
add OCR support for scanned invoices
add FastAPI backend
add Docker support
deploy the dashboard online
explore AI-assisted invoice review
```

---

## Project Log

The project is documented in:

```text
PROJECT_LOG.md
```

The log explains what was built at each milestone, why each step matters, what was learned, current limitations and the next planned improvement.

---

## Portfolio Purpose

This project is designed to show practical ability in:

```text
Python development
document processing
structured data extraction
data validation
database storage
duplicate detection
dashboard reporting
business problem-solving
clear project documentation
```

InvoicePie is intended to demonstrate how raw invoice documents can be turned into structured, validated and reviewable business data.






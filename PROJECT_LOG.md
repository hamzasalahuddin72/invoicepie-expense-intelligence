# InvoicePie Project Log

## Project Name

InvoicePie

## Repository

`invoicepie-expense-intelligence`

## Project Purpose

InvoicePie is an AI-powered invoice and expense intelligence system designed to extract structured data from invoice PDFs, validate missing or suspicious fields, detect duplicate invoices, and produce business expense insights.

The aim of this project is to build a realistic end-to-end document intelligence workflow. Instead of only extracting raw text from invoices, InvoicePie will gradually turn invoice documents into clean, structured, validated and useful business data.

---

## Current Project Status

InvoicePie currently has a working local Python environment, a generated fake sample invoice PDF, PDF text extraction using PyMuPDF, and structured invoice parsing into JSON.

The current completed pipeline is:

```text
Sample invoice PDF
↓
PDF text extraction
↓
Invoice field parsing
↓
Structured JSON output
```

---

# Milestone 1 — Project Setup and First Sample Invoice

## What Was Built

The initial InvoicePie project structure was created with folders for application code, sample data, extracted JSON outputs, tests, and utility scripts.

A Python virtual environment was created and the first set of project dependencies was installed. A utility script, `scripts/create_sample_invoice.py`, was also created to generate a fake invoice PDF for testing.

The first sample invoice was generated and saved as:

```text
data/sample_invoices/hotel_invoice_001.pdf
```

## Why This Matters

A clean project setup is important because InvoicePie will grow into a multi-stage system. Separating application code, sample invoices, extracted outputs, tests, and utility scripts makes the project easier to maintain and easier for another developer or employer to understand.

Creating a fake sample invoice also avoids using private or sensitive business documents. This keeps the project safe to publish on GitHub while still allowing realistic testing.

## What I Learned

This milestone helped me understand the importance of setting up a project in a structured way before adding features. Even for a small MVP, clear folders and dependency management make the development process cleaner.

I also encountered a Windows encoding issue caused by the pound symbol in the generated invoice text. Fixing this helped me understand why file encoding matters when working with currency symbols and text data in Python.

## Current Limitations

The project currently uses only one simple fake invoice. This is enough for the first test, but it does not represent the variety of invoice formats used in the real world.

More sample invoices will be needed later to test different suppliers, categories, amounts, layouts, duplicate cases, missing fields, and suspicious values.

---

# Milestone 2 — PDF Text Extraction

## What Was Built

The file `app/extractor.py` was implemented using PyMuPDF.

A reusable function called `extract_text_from_pdf()` was added. This function takes a PDF file path, reads each page, extracts the text, and returns the extracted content as a string.

The extractor was tested using:

```text
data/sample_invoices/hotel_invoice_001.pdf
```

The test confirmed that text from the sample invoice can be extracted and printed in the terminal.

## Why This Matters

PDF text extraction is the first real document-processing step in InvoicePie. Before the system can validate invoices, detect duplicates, store records, or generate insights, it must first be able to read invoice content from a PDF file.

This milestone creates the foundation for the rest of the project.

## What I Learned

This milestone helped me understand the difference between reading a file and extracting meaningful content from a document format like PDF.

I also learned that digital PDFs are easier to process than scanned image PDFs because their text can usually be extracted directly. Scanned invoices will require OCR later, which is a more advanced step.

## Current Limitations

The extractor currently works best with text-based digital PDFs.

It does not yet handle scanned invoices, image-only invoices, handwritten content, rotated pages, complex tables, or multi-column layouts. These limitations are acceptable for the first MVP, but they will need to be considered as the project becomes more realistic.

---

# Milestone 3 — Structured Invoice Parsing

## What Was Built

The file `app/parser.py` was implemented to convert extracted invoice text into structured invoice data.

The parser currently identifies and cleans the following fields:

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

The first sample invoice was successfully parsed into structured JSON and saved as:

```text
data/extracted_json/hotel_invoice_001.json
```

## Why This Matters

This milestone turns raw PDF text into structured business data.

Raw text by itself is not enough for business use. A company needs reliable fields such as invoice number, supplier, due date and total amount before it can check payments, detect duplicates, analyse expenses, or export records into accounting workflows.

This is the first point where InvoicePie begins to behave like an invoice intelligence system rather than only a PDF reader.

## What I Learned

This step helped me understand that document intelligence is not only about extracting text. The extracted text must be cleaned, standardised and converted into reliable fields before it becomes useful.

I also learned the importance of predictable labels, date parsing, currency cleaning and JSON structure when building a document-processing pipeline.

For example, values such as `£1,200.00` need to be cleaned before they can be treated as numbers, and UK-style dates need to be converted into a consistent format before they can be compared or validated.

## Current Limitations

The parser currently works best with clean, text-based invoices that use predictable labels such as:

```text
Invoice Number
Invoice Date
Due Date
VAT Number
Subtotal
VAT
Total
Payment Status
Category
```

It may not work well yet with messy layouts, scanned invoices, table-heavy invoices, handwritten documents, or invoices using different field names such as `Amount Due`, `Balance`, `Bill To`, or `Tax`.

These limitations will be improved later with stronger parsing logic, validation rules, more sample invoice formats, OCR support, and possibly AI-assisted extraction.

---rnrn---

# Milestone 4 — Invoice Validation

## What Was Built

The file `app/validator.py` was implemented to check whether parsed invoice data is complete, consistent and ready for business processing.

The validator currently checks whether required fields are present, whether invoice and due dates are valid, whether the due date is not earlier than the invoice date, whether subtotal, VAT and total amount values are valid, whether subtotal plus VAT matches the total amount, and whether the payment status uses an expected value.

The validation result is saved as a structured JSON report in:

```text
data/validation_reports/hotel_invoice_001_validation.json
Why This Matters

Validation is an important step because extracted invoice data cannot automatically be trusted. Even if the parser successfully finds invoice fields, the values still need to be checked before they can be used for payment decisions, dashboards, exports or duplicate detection.

This milestone adds a basic business-control layer to InvoicePie. The system can now report whether an invoice appears complete, whether it needs review, and which issues were found.

What I Learned

This step helped me understand that invoice intelligence is not only about extraction and parsing. A useful invoice-processing system also needs validation checks that protect a business from missing fields, incorrect totals, invalid dates and unclear payment information.

I also learned how validation reports make the system more explainable. Instead of only returning a pass or fail result, the report lists each issue with a field name, severity and message. This makes the output easier for a user or reviewer to understand.

Current Limitations

The validator currently uses rule-based checks. This is useful for predictable invoice issues, but it does not yet detect more complex risks such as duplicate invoices, unusual supplier behaviour, suspicious price changes or inconsistent line-item details.

The system also depends on the parser producing clean structured fields. If the parser misses a value or extracts it incorrectly, the validator can only check the data it receives.

Next Step

The next development step is to build duplicate detection so InvoicePie can identify possible duplicate invoices using supplier name, invoice number, invoice date and total amount.

Milestone 5 will only be added to this log after duplicate detection has been implemented, tested and committed.

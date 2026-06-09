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

InvoicePie currently has a working local Python environment, a generated fake sample invoice PDF, PDF text extraction using PyMuPDF, structured invoice parsing into JSON, invoice validation report generation, duplicate invoice detection, SQLite database storage, a Streamlit dashboard for expense insights, and improved GitHub project documentation.

The current completed pipeline is:

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
Streamlit dashboard
↓
GitHub README documentation
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

---

# Milestone 4 — Invoice Validation

## What Was Built

The file `app/validator.py` was implemented to check whether parsed invoice data is complete, consistent and ready for business processing.

The validator currently checks whether required fields are present, whether invoice and due dates are valid, whether the due date is not earlier than the invoice date, whether subtotal, VAT and total amount values are valid, whether subtotal plus VAT matches the total amount, and whether the payment status uses an expected value.

The validation result is saved as a structured JSON report in:

```text
data/validation_reports/hotel_invoice_001_validation.json
```

## Why This Matters

Validation is an important step because extracted invoice data cannot automatically be trusted. Even if the parser successfully finds invoice fields, the values still need to be checked before they can be used for payment decisions, dashboards, exports or duplicate detection.

This milestone adds a basic business-control layer to InvoicePie. The system can now report whether an invoice appears complete, whether it needs review, and which issues were found.

## What I Learned

This step helped me understand that invoice intelligence is not only about extraction and parsing. A useful invoice-processing system also needs validation checks that protect a business from missing fields, incorrect totals, invalid dates and unclear payment information.

I also learned how validation reports make the system more explainable. Instead of only returning a pass or fail result, the report lists each issue with a field name, severity and message. This makes the output easier for a user or reviewer to understand.

## Current Limitations

The validator currently uses rule-based checks. This is useful for predictable invoice issues, but it does not yet detect more complex risks such as duplicate invoices, unusual supplier behaviour, suspicious price changes or inconsistent line-item details.

The system also depends on the parser producing clean structured fields. If the parser misses a value or extracts it incorrectly, the validator can only check the data it receives.

---

---

# Milestone 5 — Duplicate Invoice Detection

## What Was Built

The file `app/duplicate_detector.py` was implemented to compare parsed invoice JSON records and identify possible duplicate invoices.

The duplicate detector currently loads invoice records from:

```text
data/extracted_json/
```

It compares invoice pairs using supplier name, invoice number, invoice date, due date and total amount. Each match is given a similarity score and a match type such as `possible_duplicate` or `likely_duplicate`.

To test the feature, two additional sample invoice JSON files were added:

```text
data/extracted_json/hotel_invoice_001_duplicate.json
data/extracted_json/transport_invoice_001.json
```

The duplicate detection report is saved as:

```text
data/duplicate_reports/duplicate_report.json
```

The test successfully detected one likely duplicate between the original hotel invoice and the duplicate hotel invoice copy.

## Why This Matters

Duplicate detection is a valuable business-control feature because duplicate supplier invoices can lead to accidental double payments.

This milestone moves InvoicePie beyond extraction and validation. The system can now compare multiple invoice records and flag records that may need review before payment processing.

## What I Learned

This step helped me understand how duplicate detection can be built using simple but explainable rule-based scoring.

I learned that matching only one field is not enough. A stronger duplicate signal comes from combining multiple fields such as supplier name, invoice number, total amount and invoice dates.

I also encountered a UTF-8 BOM issue when loading JSON files created on Windows. Updating the JSON reader to use `utf-8-sig` made the duplicate detector more robust when handling files saved with different encoding behaviour.

## Current Limitations

The duplicate detector currently uses rule-based scoring. This works well for clear duplicate cases where supplier name, invoice number and totals match exactly.

It may not detect more complex duplicates where supplier names are slightly different, invoice numbers have formatting differences, dates are missing, or totals vary because of partial payments or currency conversion.

The current test records are also small and simple. More sample invoices will be needed later to test realistic duplicate and near-duplicate cases.

---

---

# Milestone 6 — Database Storage

## What Was Built

The file `app/database.py` was implemented to store InvoicePie outputs in a local SQLite database.

The database currently creates and manages three tables:

```text
invoices
validation_reports
duplicate_matches
```

The script imports parsed invoice records from:

```text
data/extracted_json/
```

It imports validation reports from:

```text
data/validation_reports/
```

It imports duplicate detection matches from:

```text
data/duplicate_reports/
```

The local SQLite database is created at:

```text
data/database/invoicepie.db
```

The latest database import successfully stored:

```text
3 invoice records
1 validation report
1 duplicate match
```

## Why This Matters

Database storage is an important step because JSON files are useful for early development, but they are not enough for a realistic business system.

By moving parsed invoices, validation reports and duplicate matches into structured database tables, InvoicePie becomes easier to query, analyse and extend. This prepares the project for dashboard reporting, filtering, search, analytics and future API development.

This milestone also shows that the system is moving from separate scripts into a more complete data-processing workflow.

## What I Learned

This step helped me understand how extracted and processed document data can be organised into database tables.

I also learned why separating invoices, validation reports and duplicate matches into different tables makes the data cleaner and easier to work with. Each table has a clear responsibility, which supports better reporting and future development.

Using SQLite also helped me build database functionality quickly without needing external database setup at this stage. This keeps the project lightweight while still proving the core storage workflow.

## Current Limitations

The project currently uses SQLite for local development. This is suitable for a portfolio MVP, but a production version would likely use PostgreSQL or a managed cloud database.

The database import script currently resets tables before importing sample data, which is useful for repeatable testing but not suitable for a real live system.

The current schema is also simple. It does not yet include user accounts, supplier master records, payment tracking history, line-item tables, audit logs or dashboard-ready summary views.

---

---

# Milestone 7 — Dashboard and Expense Insights

## What Was Built

The file `app/dashboard.py` was implemented using Streamlit to display the processed InvoicePie data in a simple dashboard.

The dashboard reads from the local SQLite database at:

```text
data/database/invoicepie.db
```

It currently displays:

```text
summary metrics
total invoice count
total spend
unpaid invoice count
validation issue count
duplicate match count
spend by category
spend by supplier
stored invoice records
validation reports
duplicate invoice warnings
```

The dashboard was tested locally using:

```text
python -m streamlit run app/dashboard.py
```

The current dashboard successfully shows 3 invoice records, £2,760.00 total spend, 3 unpaid invoices, 0 validation issues and 1 duplicate match.

## Why This Matters

The dashboard makes the project easier to understand because it turns processed invoice data into visible business insight.

Before this milestone, InvoicePie produced JSON files and database records. Those outputs are useful technically, but they are not easy for a business user to review. The dashboard gives users a clearer view of invoice totals, supplier spend, payment status, validation results and duplicate warnings.

This milestone helps connect the backend document-processing pipeline to a user-facing reporting layer.

## What I Learned

This step helped me understand how database records can be turned into useful dashboard views using pandas and Streamlit.

I also learned that the way data is presented matters. A working backend is important, but employers and users need to quickly see what the system does and why it is useful.

The dashboard also made the earlier pipeline easier to verify because the invoice records, validation report and duplicate match can now be checked visually in one place.

## Current Limitations

The dashboard is currently a local Streamlit app and is not deployed online yet.

It reads from a local SQLite database, so the database must be generated first by running `python app/database.py`.

The current dashboard uses a small sample dataset, so the charts are simple. More invoice records will be needed later to make the spend insights more realistic.

The dashboard also does not yet include filters, upload functionality, authentication, export buttons or AI-assisted natural-language invoice review.

---

---

# Milestone 8 — README and GitHub Presentation

## What Was Built

The project `README.md` was rewritten to explain InvoicePie more clearly for GitHub visitors and potential employers.

The README now includes:

```text
project overview
current pipeline
implemented features
tech stack
project structure
local setup instructions
run commands
example output
current limitations
planned improvements
portfolio purpose
```

A `.streamlit/config.toml` file was also added to disable Streamlit usage statistics for the local project environment.

A `docs/screenshots/` folder was created so dashboard screenshots can be added later as the visual presentation of the project improves.

## Why This Matters

A strong README is important because many employers and technical reviewers will look at the GitHub page before running the project.

The code shows what the system does technically, but the README explains the project purpose, workflow, features and business value. This makes the project easier to understand quickly and improves the first impression of the repository.

## What I Learned

This milestone helped me understand that project presentation is part of software engineering.

A portfolio project should not only work locally. It should also be easy for someone else to understand, set up and review. Clear documentation helps connect the technical implementation to the business problem the project is trying to solve.

I also learned that documenting current limitations is useful because it shows awareness of what the system can and cannot do yet.

## Current Limitations

The README explains the current project well, but it does not yet include actual dashboard screenshots.

The project also does not yet have automated tests, deployment instructions, architecture diagrams or a hosted demo link.

These will be added later as the project becomes more complete.

---

## Next Step

The next development step is to add more varied sample invoices, including invalid and suspicious invoice examples, so the validation and duplicate detection features can be tested against more realistic cases.

Milestone 9 will only be added to this log after the expanded sample invoice set has been created, tested and committed.

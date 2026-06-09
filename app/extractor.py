import fitz
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a digital PDF invoice using PyMuPDF.

    This first version supports text-based PDFs. Scanned image invoices
    will need OCR later in the project.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    extracted_text = []

    with fitz.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text()
            extracted_text.append(f"\n--- Page {page_number} ---\n")
            extracted_text.append(page_text)

    return "".join(extracted_text).strip()


if __name__ == "__main__":
    sample_pdf = "data/sample_invoices/hotel_invoice_001.pdf"

    text = extract_text_from_pdf(sample_pdf)

    print("\nExtracted invoice text:\n")
    print(text)

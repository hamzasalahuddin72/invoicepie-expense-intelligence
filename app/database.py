import json
import sqlite3
from pathlib import Path
from typing import Any


DATABASE_PATH = "data/database/invoicepie.db"


def load_json_file(path: Path) -> dict:
    """
    Load a JSON file safely, including files saved with a UTF-8 BOM on Windows.
    """
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def connect_database(database_path: str = DATABASE_PATH) -> sqlite3.Connection:
    """
    Connect to the SQLite database and ensure the parent folder exists.
    """
    db_path = Path(database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(db_path)


def create_tables(connection: sqlite3.Connection) -> None:
    """
    Create database tables for invoices, validation reports and duplicate matches.
    """
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT,
            invoice_number TEXT,
            invoice_date TEXT,
            due_date TEXT,
            vat_number TEXT,
            subtotal REAL,
            vat_amount REAL,
            total_amount REAL,
            payment_status TEXT,
            category TEXT,
            currency TEXT,
            source_file TEXT UNIQUE,
            record_file TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS validation_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            invoice_number TEXT,
            supplier_name TEXT,
            validation_status TEXT,
            total_issues INTEGER,
            high_risk_issues INTEGER,
            medium_risk_issues INTEGER,
            issues_json TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS duplicate_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_type TEXT,
            similarity_score INTEGER,
            record_a_file TEXT,
            record_b_file TEXT,
            supplier_a TEXT,
            supplier_b TEXT,
            invoice_number_a TEXT,
            invoice_number_b TEXT,
            total_amount_a REAL,
            total_amount_b REAL,
            reasons_json TEXT
        )
        """
    )

    connection.commit()


def reset_tables(connection: sqlite3.Connection) -> None:
    """
    Clear existing sample data so the import script can be run repeatedly.
    """
    cursor = connection.cursor()

    cursor.execute("DELETE FROM invoices")
    cursor.execute("DELETE FROM validation_reports")
    cursor.execute("DELETE FROM duplicate_matches")

    connection.commit()


def insert_invoice(connection: sqlite3.Connection, invoice: dict, record_file: str) -> None:
    """
    Insert a parsed invoice record into the invoices table.
    """
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO invoices (
            supplier_name,
            invoice_number,
            invoice_date,
            due_date,
            vat_number,
            subtotal,
            vat_amount,
            total_amount,
            payment_status,
            category,
            currency,
            source_file,
            record_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            invoice.get("supplier_name"),
            invoice.get("invoice_number"),
            invoice.get("invoice_date"),
            invoice.get("due_date"),
            invoice.get("vat_number"),
            invoice.get("subtotal"),
            invoice.get("vat_amount"),
            invoice.get("total_amount"),
            invoice.get("payment_status"),
            invoice.get("category"),
            invoice.get("currency"),
            invoice.get("source_file"),
            record_file,
        ),
    )

    connection.commit()


def insert_validation_report(connection: sqlite3.Connection, report: dict) -> None:
    """
    Insert a validation report into the validation_reports table.
    """
    cursor = connection.cursor()
    summary = report.get("summary", {})

    cursor.execute(
        """
        INSERT INTO validation_reports (
            source_file,
            invoice_number,
            supplier_name,
            validation_status,
            total_issues,
            high_risk_issues,
            medium_risk_issues,
            issues_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report.get("source_file"),
            report.get("invoice_number"),
            report.get("supplier_name"),
            report.get("validation_status"),
            summary.get("total_issues"),
            summary.get("high_risk_issues"),
            summary.get("medium_risk_issues"),
            json.dumps(report.get("issues", []), ensure_ascii=False),
        ),
    )

    connection.commit()


def insert_duplicate_match(connection: sqlite3.Connection, match: dict) -> None:
    """
    Insert one duplicate match into the duplicate_matches table.
    """
    cursor = connection.cursor()

    record_a = match.get("record_a", {})
    record_b = match.get("record_b", {})

    cursor.execute(
        """
        INSERT INTO duplicate_matches (
            match_type,
            similarity_score,
            record_a_file,
            record_b_file,
            supplier_a,
            supplier_b,
            invoice_number_a,
            invoice_number_b,
            total_amount_a,
            total_amount_b,
            reasons_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            match.get("match_type"),
            match.get("similarity_score"),
            record_a.get("record_file"),
            record_b.get("record_file"),
            record_a.get("supplier_name"),
            record_b.get("supplier_name"),
            record_a.get("invoice_number"),
            record_b.get("invoice_number"),
            record_a.get("total_amount"),
            record_b.get("total_amount"),
            json.dumps(match.get("reasons", []), ensure_ascii=False),
        ),
    )

    connection.commit()


def import_invoice_records(connection: sqlite3.Connection, folder_path: str) -> int:
    """
    Import parsed invoice JSON records into the database.
    """
    folder = Path(folder_path)
    count = 0

    for json_file in sorted(folder.glob("*.json")):
        invoice = load_json_file(json_file)
        insert_invoice(connection, invoice, json_file.name)
        count += 1

    return count


def import_validation_reports(connection: sqlite3.Connection, folder_path: str) -> int:
    """
    Import validation report JSON files into the database.
    """
    folder = Path(folder_path)
    count = 0

    if not folder.exists():
        return count

    for json_file in sorted(folder.glob("*.json")):
        report = load_json_file(json_file)
        insert_validation_report(connection, report)
        count += 1

    return count


def import_duplicate_reports(connection: sqlite3.Connection, folder_path: str) -> int:
    """
    Import duplicate match records from duplicate report JSON files.
    """
    folder = Path(folder_path)
    count = 0

    if not folder.exists():
        return count

    for json_file in sorted(folder.glob("*.json")):
        report = load_json_file(json_file)

        for match in report.get("matches", []):
            insert_duplicate_match(connection, match)
            count += 1

    return count


def get_table_count(connection: sqlite3.Connection, table_name: str) -> int:
    """
    Return the number of rows in a table.
    """
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def show_database_summary(connection: sqlite3.Connection) -> dict[str, Any]:
    """
    Return a simple summary of stored database records.
    """
    return {
        "invoices": get_table_count(connection, "invoices"),
        "validation_reports": get_table_count(connection, "validation_reports"),
        "duplicate_matches": get_table_count(connection, "duplicate_matches"),
    }


if __name__ == "__main__":
    connection = connect_database()

    create_tables(connection)
    reset_tables(connection)

    invoice_count = import_invoice_records(connection, "data/extracted_json")
    validation_count = import_validation_reports(connection, "data/validation_reports")
    duplicate_match_count = import_duplicate_reports(connection, "data/duplicate_reports")

    summary = show_database_summary(connection)

    connection.close()

    print("InvoicePie database import completed.")
    print(f"Invoices imported: {invoice_count}")
    print(f"Validation reports imported: {validation_count}")
    print(f"Duplicate matches imported: {duplicate_match_count}")
    print("\nDatabase summary:")
    print(json.dumps(summary, indent=4))
    print(f"\nDatabase saved locally at: {DATABASE_PATH}")

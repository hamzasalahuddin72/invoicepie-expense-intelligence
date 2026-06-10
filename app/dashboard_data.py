from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

from database import (
    connect_database,
    create_tables,
    reset_tables,
    import_invoice_records,
    import_validation_reports,
    import_duplicate_reports,
)


DATABASE_PATH = Path("data/database/invoicepie.db")


def ensure_database_exists():
    if DATABASE_PATH.exists():
        return

    connection = connect_database(str(DATABASE_PATH))

    create_tables(connection)
    reset_tables(connection)
    import_invoice_records(connection, "data/extracted_json")
    import_validation_reports(connection, "data/validation_reports")
    import_duplicate_reports(connection, "data/duplicate_reports")

    connection.close()


@st.cache_data
def load_table(table_name):
    allowed_tables = ["invoices", "validation_reports", "duplicate_matches"]

    if table_name not in allowed_tables:
        raise ValueError(f"Table not allowed: {table_name}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql_query(query, connection)


def load_dashboard_data():
    ensure_database_exists()

    invoices = load_table("invoices")
    validation_reports = load_table("validation_reports")
    duplicate_matches = load_table("duplicate_matches")

    invoices = add_review_columns(invoices, validation_reports, duplicate_matches)

    return invoices, validation_reports, duplicate_matches


def add_review_columns(invoices, validation_reports, duplicate_matches):
    invoices = invoices.copy()

    if invoices.empty:
        return invoices

    invoices = add_validation_columns(invoices, validation_reports)
    invoices = add_duplicate_risk_column(invoices, duplicate_matches)

    return invoices


def add_validation_columns(invoices, validation_reports):
    if validation_reports.empty:
        invoices["validation_status"] = "not_validated"
        invoices["total_issues"] = 0
        invoices["high_risk_issues"] = 0
        invoices["medium_risk_issues"] = 0
        return invoices

    columns = [
        "source_file",
        "validation_status",
        "total_issues",
        "high_risk_issues",
        "medium_risk_issues",
    ]

    available_columns = [column for column in columns if column in validation_reports.columns]

    invoices = invoices.merge(
        validation_reports[available_columns],
        on="source_file",
        how="left",
    )

    invoices["validation_status"] = invoices["validation_status"].fillna("not_validated")
    invoices["total_issues"] = invoices["total_issues"].fillna(0)
    invoices["high_risk_issues"] = invoices["high_risk_issues"].fillna(0)
    invoices["medium_risk_issues"] = invoices["medium_risk_issues"].fillna(0)

    return invoices


def add_duplicate_risk_column(invoices, duplicate_matches):
    duplicate_files = set()

    if not duplicate_matches.empty:
        if "record_a_file" in duplicate_matches.columns:
            duplicate_files.update(duplicate_matches["record_a_file"].dropna().astype(str))

        if "record_b_file" in duplicate_matches.columns:
            duplicate_files.update(duplicate_matches["record_b_file"].dropna().astype(str))

    if "record_file" not in invoices.columns:
        invoices["duplicate_risk"] = "No duplicate risk"
        return invoices

    invoices["duplicate_risk"] = invoices["record_file"].astype(str).apply(
        lambda file_name: "Duplicate risk" if file_name in duplicate_files else "No duplicate risk"
    )

    return invoices


def get_unique_values(dataframe, column):
    if dataframe.empty or column not in dataframe.columns:
        return []

    values = dataframe[column].dropna().astype(str).str.strip()
    values = values[values != ""]

    return sorted(values.unique().tolist())

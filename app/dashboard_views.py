import streamlit as st

from dashboard_data import get_unique_values


def format_currency(value):
    try:
        return f"£{float(value):,.2f}"
    except (TypeError, ValueError):
        return "£0.00"


def show_filters(invoices):
    st.subheader("Review Filters")

    if invoices.empty:
        return invoices

    with st.expander("Filter invoice records", expanded=True):
        col1, col2, col3 = st.columns(3)

        suppliers = get_unique_values(invoices, "supplier_name")
        categories = get_unique_values(invoices, "category")
        payment_statuses = get_unique_values(invoices, "payment_status")

        selected_suppliers = col1.multiselect("Supplier", suppliers, default=suppliers)
        selected_categories = col2.multiselect("Category", categories, default=categories)
        selected_payment_statuses = col3.multiselect(
            "Payment Status",
            payment_statuses,
            default=payment_statuses,
        )

        col4, col5, col6 = st.columns(3)

        validation_statuses = get_unique_values(invoices, "validation_status")
        duplicate_risks = get_unique_values(invoices, "duplicate_risk")

        selected_validation_statuses = col4.multiselect(
            "Validation Status",
            validation_statuses,
            default=validation_statuses,
        )

        selected_duplicate_risks = col5.multiselect(
            "Duplicate Risk",
            duplicate_risks,
            default=duplicate_risks,
        )

        search_text = col6.text_input(
            "Search invoice number or supplier",
            placeholder="Example: INV-1001",
        )

    filtered = invoices.copy()

    filtered = filter_by_selected_values(filtered, "supplier_name", selected_suppliers)
    filtered = filter_by_selected_values(filtered, "category", selected_categories)
    filtered = filter_by_selected_values(filtered, "payment_status", selected_payment_statuses)
    filtered = filter_by_selected_values(filtered, "validation_status", selected_validation_statuses)
    filtered = filter_by_selected_values(filtered, "duplicate_risk", selected_duplicate_risks)
    filtered = filter_by_search_text(filtered, search_text)

    st.caption(f"Showing {len(filtered)} of {len(invoices)} invoice records after filters.")

    return filtered


def filter_by_selected_values(dataframe, column, selected_values):
    if not selected_values:
        return dataframe

    return dataframe[dataframe[column].astype(str).isin(selected_values)]


def filter_by_search_text(dataframe, search_text):
    if not search_text.strip():
        return dataframe

    search_value = search_text.strip().lower()

    supplier_match = dataframe["supplier_name"].astype(str).str.lower().str.contains(search_value)
    invoice_match = dataframe["invoice_number"].astype(str).str.lower().str.contains(search_value)

    return dataframe[supplier_match | invoice_match]


def show_summary_metrics(invoices):
    total_invoices = len(invoices)

    if invoices.empty:
        total_spend = 0
        unpaid_count = 0
        issue_count = 0
        duplicate_count = 0
    else:
        total_spend = invoices["total_amount"].sum()
        unpaid_count = invoices["payment_status"].str.lower().eq("unpaid").sum()
        issue_count = int(invoices["total_issues"].fillna(0).sum())
        duplicate_count = invoices["duplicate_risk"].eq("Duplicate risk").sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Invoices", total_invoices)
    col2.metric("Total Spend", format_currency(total_spend))
    col3.metric("Unpaid Invoices", int(unpaid_count))
    col4.metric("Validation Issues", int(issue_count))
    col5.metric("Duplicate Risk Records", int(duplicate_count))


def show_review_sections(invoices):
    st.subheader("Review Sections")

    if invoices.empty:
        st.info("No invoice records match the selected filters.")
        return

    needs_review = invoices[
        (invoices["validation_status"].astype(str).str.lower() != "passed")
        | (invoices["duplicate_risk"].astype(str) == "Duplicate risk")
    ]

    unpaid_invoices = invoices[
        invoices["payment_status"].astype(str).str.lower().isin(["unpaid", "pending", "overdue"])
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.write("Invoices Needing Review")
        show_simple_table(
            needs_review,
            [
                "supplier_name",
                "invoice_number",
                "validation_status",
                "total_issues",
                "duplicate_risk",
                "total_amount",
                "source_file",
            ],
            "No invoices need review in the selected filter view.",
        )

    with col2:
        st.write("Unpaid / Pending Invoices")
        show_simple_table(
            unpaid_invoices,
            [
                "supplier_name",
                "invoice_number",
                "due_date",
                "payment_status",
                "total_amount",
                "category",
                "source_file",
            ],
            "No unpaid or pending invoices in the selected filter view.",
        )


def show_expense_insights(invoices):
    st.subheader("Expense Insights")

    if invoices.empty:
        st.info("No invoice records match the selected filters.")
        return

    category_spend = (
        invoices.groupby("category")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    supplier_spend = (
        invoices.groupby("supplier_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.write("Spend by Category")
    st.bar_chart(category_spend, x="category", y="total_amount")

    st.write("Spend by Supplier")
    st.bar_chart(supplier_spend, x="supplier_name", y="total_amount")


def show_invoice_table(invoices):
    st.subheader("Filtered Invoice Records")

    show_simple_table(
        invoices,
        [
            "supplier_name",
            "invoice_number",
            "invoice_date",
            "due_date",
            "subtotal",
            "vat_amount",
            "total_amount",
            "payment_status",
            "category",
            "validation_status",
            "total_issues",
            "duplicate_risk",
            "source_file",
        ],
        "No invoice records found for the selected filters.",
    )


def show_validation_reports(validation_reports, filtered_invoices):
    st.subheader("Validation Reports")

    if validation_reports.empty:
        st.info("No validation reports found.")
        return

    source_files = set(filtered_invoices["source_file"].dropna().astype(str))

    if source_files:
        validation_reports = validation_reports[
            validation_reports["source_file"].astype(str).isin(source_files)
        ]

    show_simple_table(
        validation_reports,
        [
            "supplier_name",
            "invoice_number",
            "validation_status",
            "total_issues",
            "high_risk_issues",
            "medium_risk_issues",
            "source_file",
        ],
        "No validation reports match the selected filters.",
    )


def show_duplicate_matches(duplicate_matches, filtered_invoices):
    st.subheader("Duplicate Invoice Warnings")

    if duplicate_matches.empty:
        st.success("No duplicate matches found.")
        return

    record_files = set(filtered_invoices["record_file"].dropna().astype(str))

    if record_files:
        duplicate_matches = duplicate_matches[
            duplicate_matches["record_a_file"].astype(str).isin(record_files)
            | duplicate_matches["record_b_file"].astype(str).isin(record_files)
        ]

    show_simple_table(
        duplicate_matches,
        [
            "match_type",
            "similarity_score",
            "record_a_file",
            "record_b_file",
            "supplier_a",
            "supplier_b",
            "invoice_number_a",
            "invoice_number_b",
            "total_amount_a",
            "total_amount_b",
        ],
        "No duplicate matches found for the selected filters.",
    )


def show_simple_table(dataframe, columns, empty_message):
    if dataframe.empty:
        st.info(empty_message)
        return

    available_columns = [column for column in columns if column in dataframe.columns]
    st.dataframe(dataframe[available_columns], width="stretch")

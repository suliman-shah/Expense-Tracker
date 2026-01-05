import streamlit as st
import json
import pandas as pd
from datetime import date
import os
import plotly.express as px

# Configure page
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add Font Awesome icons
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .icon-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# File path for expenses data
EXPENSES_FILE = "./data/expenses.json"

# Ensure data directory exists
os.makedirs(os.path.dirname(EXPENSES_FILE), exist_ok=True)


def load_expenses():
    """Load expenses from JSON file."""
    try:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r") as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_expenses(expenses):
    """Save expenses to JSON file."""
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=4)


def validate_category(category):
    """Validate category input."""
    if not category:
        return False, "Category cannot be empty."
    if not category.isalpha():
        return False, "Category must contain only letters."
    return True, ""


def validate_amount(amount):
    """Validate amount input."""
    try:
        if amount <= 0:
            return False, "Amount must be greater than 0."
        return True, ""
    except (ValueError, TypeError):
        return False, "Amount must be a valid number."


def validate_description(description):
    """Validate description input."""
    if not description:
        return False, "Description cannot be empty."
    if len(description) < 5:
        return False, "Description must be at least 5 characters."
    return True, ""


def add_expense_page():
    """Page for adding new expenses."""
    st.markdown('<div class="icon-header"><i class="fas fa-plus-circle" style="font-size: 1.5rem; color: #4CAF50;"></i><h2 style="margin: 0;">Add New Expense</h2></div>', unsafe_allow_html=True)

    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            category = st.text_input(
                "Expense Category",
                placeholder="e.g., Food, Transport, Utility",
                help="Enter the category for this expense"
            )

        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=1.0,
                help="Enter the expense amount"
            )

        description = st.text_area(
            "Description",
            placeholder="Describe what the expense is for",
            help="Minimum 5 characters required"
        )

        expense_date = st.date_input(
            "Date",
            value=date.today(),
            help="Select the date of the expense"
        )

        if st.form_submit_button("Save Expense", use_container_width=True):
            # Validate inputs
            is_valid_category, category_error = validate_category(category)
            is_valid_amount, amount_error = validate_amount(amount)
            is_valid_description, desc_error = validate_description(
                description)

            if not is_valid_category:
                st.error(category_error)
            elif not is_valid_amount:
                st.error(amount_error)
            elif not is_valid_description:
                st.error(desc_error)
            else:
                # Add expense
                expenses = load_expenses()
                expenses.append({
                    "Category": category.capitalize(),
                    "Amount": int(amount),
                    "Description": description,
                    "Date": str(expense_date)
                })
                save_expenses(expenses)
                st.success("Expense added successfully!")
                st.balloons()


def view_all_expenses_page():
    """Page for viewing all expenses."""
    st.markdown('<div class="icon-header"><i class="fas fa-chart-bar" style="font-size: 1.5rem; color: #2196F3;"></i><h2 style="margin: 0;">All Expenses</h2></div>', unsafe_allow_html=True)

    expenses = load_expenses()

    if not expenses:
        st.info("No expenses recorded yet. Add one to get started!")
        return

    # Create DataFrame
    df = pd.DataFrame(expenses)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=False)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Spent", f"PKR {df['Amount'].sum():,}")
    with col2:
        st.metric("Number of Expenses", len(df))
    with col3:
        st.metric("Average Expense", f"PKR {df['Amount'].mean():.2f}")

    st.divider()

    # Display table
    st.subheader("Expense Details")
    display_df = df[['Date', 'Category', 'Description', 'Amount']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df['Amount'] = display_df['Amount'].apply(lambda x: f"PKR {x:,}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Chart
    st.subheader("Expense Trend")
    chart_df = df.sort_values('Date')
    chart_df['Cumulative'] = chart_df['Amount'].cumsum()
    st.line_chart(chart_df.set_index('Date')['Cumulative'])


def view_by_category_page():
    """Page for viewing expenses by category."""
    st.markdown('<div class="icon-header"><i class="fas fa-tags" style="font-size: 1.5rem; color: #FF9800;"></i><h2 style="margin: 0;">Expenses by Category</h2></div>', unsafe_allow_html=True)

    expenses = load_expenses()

    if not expenses:
        st.info("No expenses recorded yet. Add one to get started!")
        return

    df = pd.DataFrame(expenses)

    # Get unique categories
    categories = sorted(df['Category'].unique())

    # Select category
    selected_category = st.selectbox(
        "Select Category",
        categories,
        help="Choose a category to view its expenses"
    )

    # Filter by category
    category_df = df[df['Category'] == selected_category].copy()
    category_df['Date'] = pd.to_datetime(category_df['Date'])
    category_df = category_df.sort_values('Date', ascending=False)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Total in {selected_category}",
                  f"PKR {category_df['Amount'].sum():,}")
    with col2:
        st.metric("Number of Expenses", len(category_df))
    with col3:
        st.metric("Average Expense", f"PKR {category_df['Amount'].mean():.2f}")

    st.divider()

    # Display table
    st.subheader(f"All {selected_category} Expenses")
    display_df = category_df[['Date', 'Description', 'Amount']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df['Amount'] = display_df['Amount'].apply(lambda x: f"PKR {x:,}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Category breakdown
    st.subheader("Category Distribution")
    category_summary = df.groupby(
        'Category')['Amount'].sum().sort_values(ascending=False)
    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(category_summary)
    with col2:
        fig = px.pie(values=category_summary.values,
                     names=category_summary.index, title="Category Distribution")
        st.plotly_chart(fig, use_container_width=True)


def analytics_page():
    """Page for expense analytics."""
    st.markdown('<div class="icon-header"><i class="fas fa-chart-line" style="font-size: 1.5rem; color: #9C27B0;"></i><h2 style="margin: 0;">Analytics</h2></div>', unsafe_allow_html=True)

    expenses = load_expenses()

    if not expenses:
        st.info("No expenses recorded yet. Add one to get started!")
        return

    df = pd.DataFrame(expenses)
    df['Date'] = pd.to_datetime(df['Date'])

    # Summary statistics
    st.subheader("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Expenses", len(df))
    with col2:
        st.metric("Total Spent", f"PKR {df['Amount'].sum():,}")
    with col3:
        st.metric("Average per Expense", f"PKR {df['Amount'].mean():.2f}")
    with col4:
        st.metric("Highest Expense", f"PKR {df['Amount'].max():,}")

    st.divider()

    # Category analysis
    st.subheader("Expense by Category")
    category_totals = df.groupby('Category')['Amount'].agg(
        ['sum', 'count', 'mean']).sort_values('sum', ascending=False)
    category_totals.columns = ['Total', 'Count', 'Average']
    category_totals['Total'] = category_totals['Total'].apply(
        lambda x: f"PKR {x:,}")
    category_totals['Average'] = category_totals['Average'].apply(
        lambda x: f"PKR {x:.2f}")

    st.dataframe(category_totals, use_container_width=True)

    # Monthly trends
    st.subheader("Monthly Trend")
    monthly_df = df.copy()
    monthly_df['Month'] = monthly_df['Date'].dt.to_period('M')
    monthly_summary = monthly_df.groupby('Month')['Amount'].sum()
    monthly_display = monthly_summary.reset_index()
    monthly_display.columns = ['Month', 'Amount']
    monthly_display['Amount'] = monthly_display['Amount'].apply(lambda x: f"PKR {x:,}")
    st.dataframe(monthly_display, use_container_width=True, hide_index=True)

    # Top categories pie chart
    st.subheader("Category Distribution")
    category_dist = df.groupby('Category')['Amount'].sum()
    fig = px.pie(values=category_dist.values,
                 names=category_dist.index, title="Category Distribution")
    st.plotly_chart(fig, use_container_width=True)


def manage_expenses_page():
    """Page for managing (deleting) expenses."""
    st.markdown('<div class="icon-header"><i class="fas fa-trash-alt" style="font-size: 1.5rem; color: #f44336;"></i><h2 style="margin: 0;">Manage Expenses</h2></div>', unsafe_allow_html=True)

    expenses = load_expenses()

    if not expenses:
        st.info("No expenses recorded yet. Nothing to delete!")
        return

    # Create DataFrame
    df = pd.DataFrame(expenses)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=False)

    st.subheader("Delete Individual Expenses")
    
    # Create a display dataframe with an index
    display_df = df[['Date', 'Category', 'Description', 'Amount']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df['Amount'] = display_df['Amount'].apply(lambda x: f"PKR {x:,}")
    
    # Display table
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Select expense to delete
    st.markdown("<p style='font-weight: bold;'>Select an expense to delete:</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        expense_options = [f"{row['Date'].strftime('%Y-%m-%d')} | {row['Category']} | PKR {row['Amount']:,}" for _, row in df.iterrows()]
        selected_expense = st.selectbox(
            "Choose expense",
            range(len(expense_options)),
            format_func=lambda i: expense_options[i],
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Delete", use_container_width=True, key="delete_single"):
            expenses.pop(selected_expense)
            save_expenses(expenses)
            st.success("Expense deleted successfully!")
            st.rerun()
    
    st.divider()
    
    # Clear all expenses
    st.subheader("Clear All Expenses")
    st.warning(f"⚠️ You have {len(expenses)} expenses. This action cannot be undone!")
    
    if st.button("Clear All Expenses", use_container_width=True, key="clear_all"):
        if st.session_state.get('confirm_clear'):
            save_expenses([])
            st.success("All expenses cleared successfully!")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.info("Click the button again to confirm clearing all expenses")
    
    if st.session_state.get('confirm_clear'):
        if st.button("Confirm - Clear All Expenses Permanently", use_container_width=True, key="confirm_clear_btn"):
            save_expenses([])
            st.success("All expenses cleared successfully!")
            st.session_state.confirm_clear = False
            st.rerun()


def main():
    """Main application."""
    st.markdown('<h1 style="text-align: center;"><i class="fas fa-wallet" style="color: #4CAF50;"></i> Expense Tracker</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h3 style="margin: 0;"><i class="fas fa-wallet" style="color: #4CAF50; margin-right: 0.5rem;"></i>Expense Tracker</h3>
            <p style='font-size: 0.9rem; color: gray; margin-top: 0.5rem;'>Manage your finances</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        st.markdown("<h4><i class='fas fa-bars'></i> Navigation</h4>", unsafe_allow_html=True)
        
        page = st.radio(
            "Select Page",
            ["Add Expense", "View All", "By Category", "Manage Expenses", "Analytics"],
            label_visibility="collapsed"
        )

    # Route to selected page
    if page == "Add Expense":
        add_expense_page()
    elif page == "View All":
        view_all_expenses_page()
    elif page == "By Category":
        view_by_category_page()
    elif page == "Manage Expenses":
        manage_expenses_page()
    elif page == "Analytics":
        analytics_page()

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.85rem; margin-top: 2rem;'>
        <i class='fas fa-heart' style='color: #e74c3c;'></i> Made with care | Expense Tracker v1.0
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

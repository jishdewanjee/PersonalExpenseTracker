import streamlit as st
import pandas as pd
from datetime import datetime
from expenseTrackerFinal import Expense, ExpenseStorage, BudgetManager, ExpenseTracker

# Page configuration
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if 'tracker' not in st.session_state:
    storage = ExpenseStorage()
    budget_mgr = BudgetManager()
    st.session_state.tracker = ExpenseTracker(storage, budget_mgr)
    st.session_state.tracker.loadCurrent()
    st.session_state.tracker.budgetMgr.loadBudget()

# Helper function to save expenses
def save_expenses():
    st.session_state.tracker.saveCurrent()

# Main title
st.title("💰 Personal Expense Tracker")
st.markdown("---")

# Sidebar for navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    st.markdown("")

    menu = st.radio(
        "Choose an action:",
        ["📊 Dashboard", "➕ Add Expense", "📋 View Expenses", "🗑️ Delete Expense",
         "💵 Set Budget", "📈 Category Report"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Quick stats in sidebar
    total = st.session_state.tracker.totalEx()
    budget = st.session_state.tracker.budgetMgr.monthlyBudget
    num_expenses = len(st.session_state.tracker.expenses)

    st.markdown("### 📊 Quick Stats")
    st.metric("Total Expenses", f"${total:.2f}", help="Sum of all expenses")
    st.metric("Budget", f"${budget:.2f}", help="Monthly budget limit")
    st.metric("# of Expenses", num_expenses, help="Number of recorded expenses")

    st.markdown("---")

    if st.button("💾 Save All", use_container_width=True, type="primary"):
        save_expenses()
        st.success("Expenses saved!")

# Dashboard
if menu == "📊 Dashboard":
    st.header("Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    total = st.session_state.tracker.totalEx()
    budget = st.session_state.tracker.budgetMgr.monthlyBudget
    remaining = budget - total

    with col1:
        st.metric("Total Expenses", f"${total:.2f}")

    with col2:
        st.metric("Monthly Budget", f"${budget:.2f}")

    with col3:
        if budget > 0:
            percentage = (remaining/budget)*100
            st.metric("Remaining", f"${remaining:.2f}",
                     delta=f"{percentage:.1f}%",
                     delta_color="normal" if remaining >= 0 else "off")
        else:
            st.metric("Remaining", "No budget set")

    # Budget status
    if budget > 0:
        st.markdown("---")
        if remaining < 0:
            st.error(f"⚠️ Over budget by ${abs(remaining):.2f}")
            progress = 1.0
        else:
            st.success(f"✅ You have ${remaining:.2f} remaining")
            progress = total / budget if budget > 0 else 0

        st.progress(min(progress, 1.0))

    # Recent expenses
    if st.session_state.tracker.expenses:
        st.markdown("---")
        st.subheader("Recent Expenses (Last 5)")
        recent = st.session_state.tracker.expenses[-5:][::-1]

        # Create table data
        table_data = []
        for exp in recent:
            table_data.append({
                "Date": exp.date,
                "Category": exp.category or "Uncategorized",
                "Amount": f"${exp.amount:.2f}",
                "Description": exp.description or "-"
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Add Expense
elif menu == "➕ Add Expense":
    st.header("Add New Expense")

    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", value=datetime.now())
            category = st.text_input("Category (optional)")

        with col2:
            amount = st.number_input("Amount ($)", min_value=0.0, step=0.01, format="%.2f")
            description = st.text_input("Description (optional)")

        submitted = st.form_submit_button("Add Expense", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                date_str = date.strftime("%Y-%m-%d")
                new_expense = Expense(date_str, category, amount, description)
                st.session_state.tracker.expenses.append(new_expense)
                save_expenses()
                st.success("✅ Expense added successfully!")
                st.balloons()

# View Expenses
elif menu == "📋 View Expenses":
    st.header("All Expenses")

    if not st.session_state.tracker.expenses:
        st.info("No expenses recorded yet. Add your first expense!")
    else:
        # Display total
        total = st.session_state.tracker.totalEx()
        st.metric("Total", f"${total:.2f}")

        st.markdown("---")

        # Create table data
        table_data = []
        for i, exp in enumerate(st.session_state.tracker.expenses, 1):
            table_data.append({
                "#": i,
                "Date": exp.date,
                "Category": exp.category or "Uncategorized",
                "Amount": f"${exp.amount:.2f}",
                "Description": exp.description or "-"
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Delete Expense
elif menu == "🗑️ Delete Expense":
    st.header("Delete Expense")

    if not st.session_state.tracker.expenses:
        st.info("No expenses to delete.")
    else:
        st.write("Select an expense to delete:")

        # Create selection options
        expense_options = []
        for i, exp in enumerate(st.session_state.tracker.expenses, 1):
            option = f"#{i} - {exp.date} | {exp.category or 'Uncategorized'} | ${exp.amount:.2f} | {exp.description or '-'}"
            expense_options.append(option)

        selected = st.selectbox("Choose expense:", expense_options)

        if st.button("Delete Selected Expense", type="primary"):
            index = expense_options.index(selected)
            deleted = st.session_state.tracker.expenses.pop(index)
            save_expenses()
            st.success(f"Deleted: {deleted.category or 'Uncategorized'} - ${deleted.amount:.2f}")
            st.rerun()

# Set Budget
elif menu == "💵 Set Budget":
    st.header("Set Monthly Budget")

    current_budget = st.session_state.tracker.budgetMgr.monthlyBudget

    if current_budget > 0:
        st.info(f"Current budget: ${current_budget:.2f}")

    with st.form("budget_form"):
        new_budget = st.number_input(
            "Monthly Budget ($)",
            min_value=0.0,
            value=float(current_budget),
            step=10.0,
            format="%.2f"
        )

        submitted = st.form_submit_button("Set Budget", use_container_width=True)

        if submitted:
            st.session_state.tracker.budgetMgr.monthlyBudget = new_budget
            st.session_state.tracker.budgetMgr.saveBudget()
            st.success(f"✅ Budget set to ${new_budget:.2f}")

# Category Report
elif menu == "📈 Category Report":
    st.header("Expenses by Category")

    if not st.session_state.tracker.expenses:
        st.info("No expenses recorded yet.")
    else:
        # Calculate category totals
        categories = {}
        for exp in st.session_state.tracker.expenses:
            cat = exp.category.strip() if exp.category else "Uncategorized"
            categories.setdefault(cat, 0.0)
            categories[cat] += exp.amount

        # Sort categories
        sorted_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))

        # Display as metrics
        col1, col2 = st.columns(2)

        for i, (cat, amount) in enumerate(sorted_categories.items()):
            with col1 if i % 2 == 0 else col2:
                st.metric(cat, f"${amount:.2f}")

        st.markdown("---")

        # Bar chart
        st.bar_chart(sorted_categories)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Personal Expense Tracker | Made with Streamlit 🚀
    </div>
    """,
    unsafe_allow_html=True
)

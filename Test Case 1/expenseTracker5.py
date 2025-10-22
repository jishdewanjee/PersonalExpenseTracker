"""
Personal Expense Tracker — Beginner-Friendly, OOP, Modular
=========================================================

Highlights
- Clear, beginner-friendly Python with OOP and error handling
- Modular classes so you can extend features easily
- Methods/functions are written in CamelCase as requested
- CSV-based persistence for expenses, and JSON-based persistence for budget

Suggested extensions (easy to add later):
- EditExpense
- FilterByDateRange
- ImportFromOtherCsv
- SimpleReports (weekly/monthly)

Run this file directly to use the interactive menu.
"""

import csv
import json
from datetime import datetime
import os


# =========================================================
# DATA MODEL: Defines the structure of one Expense entry
# =========================================================
class Expense:
    def __init__(self, date, category, amount, description):
        self.date = date
        self.category = category
        self.amount = amount
        self.description = description

    # Convert Expense object → dictionary (for saving to CSV)
    def ToDict(self):
        return {
            "date": self.date,
            "category": self.category,
            # Use basic string formatting (no f-string format specifier)
            "amount": "{:.2f}".format(self.amount),
            "description": self.description,
        }

    # Create an Expense object from a dictionary (for reading from CSV)
    # (No @staticmethod; called as Expense.FromDict(row))
    def FromDict(data):
        return Expense(
            date=data.get("date", ""),
            category=data.get("category", ""),
            amount=float(data.get("amount", 0.0)),
            description=data.get("description", ""),
        )


# =========================================================
# STORAGE LAYER: Handles reading/writing data to files
# =========================================================
class ExpenseStorage:
    def __init__(self, csv_path="expenses.csv"):
        # CSV file where all expenses are stored
        self.csv_path = csv_path

    # Save all expenses to the CSV file
    def SaveExpensesToCsv(self, expenses):
        try:
            # Open file in write mode, overwrite existing content
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "category", "amount", "description"])
                writer.writeheader()  # Write column names
                for exp in expenses:
                    writer.writerow(exp.ToDict())
            print("Saved {} expense(s) to '{}'.".format(len(expenses), self.csv_path))
        except Exception as e:
            print("Error while saving to CSV: {}".format(e))

    # Load all expenses from CSV file and return them as Expense objects
    def LoadExpensesFromCsv(self):
        expenses = []
        if not os.path.exists(self.csv_path):
            # If file doesn't exist yet, return empty list
            return expenses
        try:
            with open(self.csv_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Convert each CSV row → Expense object
                        expense = Expense.FromDict(row)
                        expenses.append(expense)
                    except ValueError:
                        # Skip rows with invalid data instead of crashing
                        continue
        except Exception as e:
            print("Error while loading from CSV: {}".format(e))
        return expenses


# =========================================================
# BUDGET MANAGER: Manages monthly budget and comparisons
# =========================================================
class BudgetManager:
    def __init__(self, budget_json_path="budget.json"):
        self.budget_json_path = budget_json_path
        self.monthly_budget = 0.0  # Default if none set

    # Load budget amount from the JSON file when the program starts
    def LoadBudgetOnStart(self):
        if not os.path.exists(self.budget_json_path):
            return
        try:
            with open(self.budget_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.monthly_budget = float(data.get("monthly_budget", 0.0))
        except Exception as e:
            print("Error while loading budget: {}".format(e))

    # Save the current budget amount to JSON file
    def SaveBudget(self):
        try:
            with open(self.budget_json_path, "w", encoding="utf-8") as f:
                json.dump({"monthly_budget": self.monthly_budget}, f)
        except Exception as e:
            print("Error while saving budget: {}".format(e))

    # Interactive method: lets user enter and save a new monthly budget
    def SetMonthlyBudget(self):
        while True:
            raw = input("Enter your monthly budget amount: ")
            try:
                value = float(raw)
                if value < 0:
                    print("Budget cannot be negative. Try again.")
                    continue
                # Save and confirm
                self.monthly_budget = value
                self.SaveBudget()
                print("Monthly budget set to {:.2f}.".format(self.monthly_budget))
                break
            except ValueError:
                print("Please enter a valid number for the budget.")

    # Compare total expenses vs budget and show how much is left or exceeded
    def TrackBudget(self, total_expenses):
        if self.monthly_budget <= 0:
            print("No monthly budget set yet. Please set one first.")
            return
        remaining = self.monthly_budget - total_expenses
        print("Total Expenses: {:.2f}".format(total_expenses))
        print("Monthly Budget: {:.2f}".format(self.monthly_budget))
        if remaining < 0:
            print("Warning: You have exceeded your budget!")
            print("Over Budget By: {:.2f}".format(abs(remaining)))
        else:
            print("You have {:.2f} left for the month.".format(remaining))


# =========================================================
# CORE TRACKER: Business logic for adding/viewing/deleting expenses
# =========================================================
class ExpenseTracker:
    def __init__(self, storage, budget_manager):
        self.storage = storage
        self.budget_manager = budget_manager
        self.expenses = []  # All expenses currently in memory

    # Validate all input fields before adding or displaying
    def ValidateExpenseData(self, date_str, category, amount_str, description):
        # Return None if valid; otherwise return an error message
        if not date_str or not amount_str:
            return "All fields (date, category, amount, description) are required."

        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return "Date must be in YYYY-MM-DD format."

        # Validate amount is a positive number
        try:
            amount_value = float(amount_str)
            if amount_value < 0:
                return "Amount cannot be negative."
        except ValueError:
            return "Amount must be a number."

        return None  # No errors

    # Add new expense interactively through user input
    def AddExpenseInteractive(self):
        print("\nAdd a new expense:")
        date_str = input("Date (YYYY-MM-DD): ")
        category = input("Category (e.g., Food, Travel): ")
        amount_str = input("Amount: ")
        description = input("Description: ")

        # Validate user input
        error = self.ValidateExpenseData(date_str, category, amount_str, description)
        if error:
            print("Error: {}".format(error))
            return

        # Convert and save to in-memory list
        amount_value = float(amount_str)
        expense = Expense(date=date_str, category=category, amount=amount_value, description=description)
        self.expenses.append(expense)
        print("Expense added successfully.")

    # Print all expenses in a nice list
    def ViewExpenses(self):
        if not self.expenses:
            print("No expenses to show.")
            return
        print("\nYour Expenses:")

        idx = 1  # manual counter instead of enumerate(..., start=1)
        for exp in self.expenses:
            # Validate each record before printing (optional safety)
            err = self.ValidateExpenseData(exp.date, exp.category, str(exp.amount), exp.description)
            if err:
                print("Skipping invalid entry #{}: {}".format(idx, err))
                idx += 1
                continue
            print("{}. {} | {} | ${:.2f} | {}".format(idx, exp.date, exp.category, exp.amount, exp.description))
            idx += 1

    # Delete an expense by its number (index)
    def DeleteExpense(self):
        if not self.expenses:
            print("No expenses to delete.")
            return

        # Show all expenses first for reference
        self.ViewExpenses()

        try:
            index_str = input("\nEnter the expense number to delete (as shown above): ").strip()
            index = int(index_str)
            # Ensure valid range
            if index < 1 or index > len(self.expenses):
                print("Invalid number.")
                return
            # Remove selected expense
            removed = self.expenses.pop(index - 1)
            print("Deleted: {} | {} | ${:.2f} | {}".format(removed.date, removed.category, removed.amount, removed.description))
        except ValueError:
            print("Please enter a valid integer.")

    # Calculate total of all expenses
    def CalculateTotalExpenses(self):
        total = 0.0
        for exp in self.expenses:
            try:
                total += float(exp.amount)
            except (TypeError, ValueError):
                # Ignore invalid or missing amounts
                continue
        return total

    # Show a breakdown of expenses grouped by category
    def CategorizeExpenseReport(self):
        if not self.expenses:
            print("No expenses to categorize.")
            return

        category_totals = {}
        for exp in self.expenses:
            try:
                amt = float(exp.amount)
            except (TypeError, ValueError):
                continue
            # Clean up category name or mark as Uncategorized
            key = exp.category.strip() or "Uncategorized"

            # Explicit if/else instead of get(...)+sum pattern
            if key in category_totals:
                category_totals[key] = category_totals[key] + amt
            else:
                category_totals[key] = amt

        print("\nExpenses by Category:")
        # Sort categories alphabetically (simple list of tuples)
        items = list(category_totals.items())
        items.sort(key=lambda x: x[0].lower())
        for pair in items:
            cat = pair[0]
            total = pair[1]
            print("- {}: ${:.2f}".format(cat, total))

    # Save all expenses to file
    def SaveExpenses(self):
        self.storage.SaveExpensesToCsv(self.expenses)

    # Load existing expenses from file
    def LoadExpenses(self):
        self.expenses = self.storage.LoadExpensesFromCsv()


# =========================================================
# APPLICATION SHELL: The interactive menu system
# =========================================================
class ExpenseApp:
    def __init__(self):
        # Initialize all main components
        self.storage = ExpenseStorage()
        self.budget_manager = BudgetManager()
        self.tracker = ExpenseTracker(self.storage, self.budget_manager)

    # Start the app (called once at launch)
    def Start(self):
        # Load previous data (if any)
        self.tracker.LoadExpenses()
        self.budget_manager.LoadBudgetOnStart()
        print("Welcome to Personal Expense Tracker!\n")
        self.RunInteractiveMenu()

    # Show available options
    def ShowMenu(self):
        print("\nMenu:")
        print("1) Add Expense")
        print("2) View Expenses")
        print("3) Delete Expense")
        print("4) Set Monthly Budget")
        print("5) Track Budget (Calculate Total & Compare)")
        print("6) Show Category Report")
        print("7) Save Expenses")
        print("8) Exit (Auto-Save)")

    # Menu loop: keeps running until user exits
    def RunInteractiveMenu(self):
        while True:
            self.ShowMenu()
            choice = input("Choose an option (1-8): ")

            if choice == "1":
                self.tracker.AddExpenseInteractive()
            elif choice == "2":
                self.tracker.ViewExpenses()
            elif choice == "3":
                self.tracker.DeleteExpense()
            elif choice == "4":
                self.budget_manager.SetMonthlyBudget()
            elif choice == "5":
                total = self.tracker.CalculateTotalExpenses()
                self.budget_manager.TrackBudget(total)
            elif choice == "6":
                self.tracker.CategorizeExpenseReport()
            elif choice == "7":
                self.tracker.SaveExpenses()
            elif choice == "8":
                # Save automatically before exiting
                self.tracker.SaveExpenses()
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please choose 1-8.")


# =========================================================
# ENTRY POINT: Code that runs when file is executed directly
# =========================================================
if __name__ == "__main__":
    # This block runs the main code only when the file is executed directly.
    app = ExpenseApp()   # Create app instance
    app.Start()          # Launch the menu loop

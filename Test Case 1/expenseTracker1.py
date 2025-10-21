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

from __future__ import annotations
import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
import os


# -----------------------------
# Data Model
# -----------------------------
@dataclass
class Expense:
    date: str
    category: str
    amount: float
    description: str

    def ToDict(self) -> Dict[str, str]:
        return {
            "date": self.date,
            "category": self.category,
            "amount": f"{self.amount:.2f}",
            "description": self.description,
        }

    @staticmethod
    def FromDict(data: Dict[str, str]) -> "Expense":
        return Expense(
            date=data.get("date", ""),
            category=data.get("category", ""),
            amount=float(data.get("amount", 0.0)),
            description=data.get("description", ""),
        )


# -----------------------------
# Storage Layer (CSV for expenses, JSON for budget)
# -----------------------------
class ExpenseStorage:
    def __init__(self, csv_path: str = "expenses.csv") -> None:
        self.csv_path = csv_path

    def SaveExpensesToCsv(self, expenses: List[Expense]) -> None:
        try:
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "category", "amount", "description"])
                writer.writeheader()
                for exp in expenses:
                    writer.writerow(exp.ToDict())
            print(f"Saved {len(expenses)} expense(s) to '{self.csv_path}'.")
        except Exception as e:
            print(f"Error while saving to CSV: {e}")

    def LoadExpensesFromCsv(self) -> List[Expense]:
        expenses: List[Expense] = []
        if not os.path.exists(self.csv_path):
            # No file yet; return empty list without error
            return expenses
        try:
            with open(self.csv_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        expense = Expense.FromDict(row)
                        expenses.append(expense)
                    except ValueError:
                        # Skip invalid rows
                        continue
        except Exception as e:
            print(f"Error while loading from CSV: {e}")
        return expenses


class BudgetManager:
    def __init__(self, budget_json_path: str = "budget.json") -> None:
        self.budget_json_path = budget_json_path
        self.monthly_budget: float = 0.0

    def LoadBudgetOnStart(self) -> None:
        if not os.path.exists(self.budget_json_path):
            return
        try:
            with open(self.budget_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.monthly_budget = float(data.get("monthly_budget", 0.0))
        except Exception as e:
            print(f"Error while loading budget: {e}")

    def SaveBudget(self) -> None:
        try:
            with open(self.budget_json_path, "w", encoding="utf-8") as f:
                json.dump({"monthly_budget": self.monthly_budget}, f)
        except Exception as e:
            print(f"Error while saving budget: {e}")

    def SetMonthlyBudget(self) -> None:
        while True:
            raw = input("Enter your monthly budget amount: ")
            try:
                value = float(raw)
                if value < 0:
                    print("Budget cannot be negative. Try again.")
                    continue
                self.monthly_budget = value
                self.SaveBudget()
                print(f"Monthly budget set to {self.monthly_budget:.2f}.")
                break
            except ValueError:
                print("Please enter a valid number for the budget.")

    def TrackBudget(self, total_expenses: float) -> None:
        if self.monthly_budget <= 0:
            print("No monthly budget set yet. Please set one first.")
            return
        remaining = self.monthly_budget - total_expenses
        print(f"Total Expenses: {total_expenses:.2f}")
        print(f"Monthly Budget: {self.monthly_budget:.2f}")
        if remaining < 0:
            print("Warning: You have exceeded your budget!")
            print(f"Over Budget By: {abs(remaining):.2f}")
        else:
            print(f"You have {remaining:.2f} left for the month.")


# -----------------------------
# Core Tracker Logic
# -----------------------------
class ExpenseTracker:
    def __init__(self, storage: ExpenseStorage, budget_manager: BudgetManager) -> None:
        self.storage = storage
        self.budget_manager = budget_manager
        self.expenses: List[Expense] = []

    # --- Validation ---
    def ValidateExpenseData(self, date_str: str, category: str, amount_str: str, description: str) -> Optional[str]:
        # Return None if valid; otherwise return an error message string
        if not date_str or not category or not amount_str or not description: #Removing this method to avoid unnecessary info required.
            return "All fields (date, category, amount, description) are required."
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return "Date must be in YYYY-MM-DD format."
        # Validate amount
        try:
            amount_value = float(amount_str)
            if amount_value < 0:
                return "Amount cannot be negative."
        except ValueError:
            return "Amount must be a number."
        return None

    # --- CRUD ---
    def AddExpenseInteractive(self) -> None:
        print("\nAdd a new expense:")
        date_str = input("Date (YYYY-MM-DD): ")
        category = input("Category (e.g., Food, Travel): ")
        amount_str = input("Amount: ")
        description = input("Description: ")

        error = self.ValidateExpenseData(date_str, category, amount_str, description)
        if error:
            print(f"Error: {error}")
            return
        amount_value = float(amount_str)
        expense = Expense(date=date_str, category=category, amount=amount_value, description=description)
        self.expenses.append(expense)
        print("Expense added successfully.")

    def ViewExpenses(self) -> None:
        if not self.expenses:
            print("No expenses to show.")
            return
        print("\nYour Expenses:")
        for idx, exp in enumerate(self.expenses, start=1):
            # Validate before display; if invalid, skip
            err = self.ValidateExpenseData(exp.date, exp.category, str(exp.amount), exp.description)
            if err:
                print(f"Skipping invalid entry #{idx}: {err}")
                continue
            print(f"{idx}. {exp.date} | {exp.category} | ${exp.amount:.2f} | {exp.description}")

    def DeleteExpense(self) -> None:
        if not self.expenses:
            print("No expenses to delete.")
            return
        try:
            index_str = input("Enter the expense number to delete (as shown in View Expenses): ")
            index = int(index_str)
            if index < 1 or index > len(self.expenses):
                print("Invalid number.")
                return
            removed = self.expenses.pop(index - 1)
            print(f"Deleted: {removed.date} | {removed.category} | ${removed.amount:.2f} | {removed.description}")
        except ValueError:
            print("Please enter a valid integer.")

    # --- Calculations & Reports ---
    def CalculateTotalExpenses(self) -> float:
        total = 0.0
        for exp in self.expenses:
            try:
                total += float(exp.amount)
            except (TypeError, ValueError):
                # Ignore invalid amounts
                continue
        return total

    def CategorizeExpenseReport(self) -> None:
        if not self.expenses:
            print("No expenses to categorize.")
            return
        category_totals: Dict[str, float] = {}
        for exp in self.expenses:
            try:
                amt = float(exp.amount)
            except (TypeError, ValueError):
                continue
            key = exp.category.strip() or "Uncategorized"
            category_totals[key] = category_totals.get(key, 0.0) + amt

        print("\nExpenses by Category:")
        for cat, total in sorted(category_totals.items(), key=lambda x: x[0].lower()):
            print(f"- {cat}: ${total:.2f}")

    # --- Persistence ---
    def SaveExpenses(self) -> None:
        self.storage.SaveExpensesToCsv(self.expenses)

    def LoadExpenses(self) -> None:
        self.expenses = self.storage.LoadExpensesFromCsv()


# -----------------------------
# Menu / Application Shell
# -----------------------------
class ExpenseApp:
    def __init__(self) -> None:
        self.storage = ExpenseStorage()
        self.budget_manager = BudgetManager()
        self.tracker = ExpenseTracker(self.storage, self.budget_manager)

    def Start(self) -> None:
        # Load persisted data on start
        self.tracker.LoadExpenses()
        self.budget_manager.LoadBudgetOnStart()
        print("Welcome to Personal Expense Tracker!\n")
        self.RunInteractiveMenu()

    def ShowMenu(self) -> None:
        print("\nMenu:")
        print("1) Add Expense")
        print("2) View Expenses")
        print("3) Delete Expense")
        print("4) Set Monthly Budget")
        print("5) Track Budget (Calculate Total & Compare)")
        print("6) Show Category Report")
        print("7) Save Expenses")
        print("8) Exit (Auto-Save)")

    def RunInteractiveMenu(self) -> None:
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
                # Auto-save before exit
                self.tracker.SaveExpenses()
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please choose 1-8.")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    app = ExpenseApp()
    app.Start()

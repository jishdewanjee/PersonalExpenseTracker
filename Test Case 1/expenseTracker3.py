"""
Personal Expense Tracker — Beginner-Friendly, OOP, Modular
=========================================================

Revisions included (per your requests):
- Robust date validation (YYYY-MM-DD), invalid dates, and leap-year handling.
  * Any date error cancels the add operation and returns to the main menu.
- Category & Description are now optional (stored as empty strings when skipped).
- Delete Expense now shows all expenses first, then prompts for an index to delete.
- Import/Merge CSV: upload a previously saved CSV and merge it with current data (deduplicates).

Run this file directly to use the interactive menu.
"""

from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os
import calendar


# -----------------------------
# Data Model
# -----------------------------
@dataclass
class Expense:
    date: str
    category: Optional[str]
    amount: float
    description: Optional[str]

    def ToKey(self) -> Tuple[str, str, float, str]:
        """A tuple key useful for deduplication when merging CSVs."""
        return (
            self.date,
            (self.category or ""),
            float(self.amount),
            (self.description or ""),
        )

    def ToDict(self) -> Dict[str, str]:
        return {
            "date": self.date,
            "category": (self.category or ""),
            "amount": f"{float(self.amount):.2f}",
            "description": (self.description or ""),
        }

    @staticmethod
    def FromDict(data: Dict[str, str]) -> "Expense":
        # Gracefully handle missing or empty strings
        date = data.get("date", "").strip()
        category = data.get("category", "").strip() or ""
        amount_raw = (data.get("amount", "0") or "0").strip()
        description = data.get("description", "").strip() or ""
        return Expense(
            date=date,
            category=category,
            amount=float(amount_raw),
            description=description,
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

    def LoadExpensesFromCsv(self, path: Optional[str] = None) -> List[Expense]:
        target = path or self.csv_path
        expenses: List[Expense] = []
        if not os.path.exists(target):
            return expenses
        try:
            with open(target, mode="r", newline="", encoding="utf-8") as f:
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
    def _ValidateDateStrict(self, date_str: str) -> Optional[str]:
        """
        Returns None if date is valid, otherwise an error message explaining why.
        Rules:
        - Must match YYYY-MM-DD
        - Must be a real calendar date
        - If month=02 and day=29, ensure the year is leap
        """
        if not date_str:
            return "Date is required."
        # Quick shape check
        parts = date_str.split("-")
        if len(parts) != 3 or any(not p.isdigit() for p in parts):
            return "Date must be in YYYY-MM-DD format."
        y_str, m_str, d_str = parts
        if not (len(y_str) == 4 and len(m_str) == 2 and len(d_str) == 2):
            return "Date must be in YYYY-MM-DD format."
        year, month, day = int(y_str), int(m_str), int(d_str)

        # Leap-day specific check first for custom message
        if month == 2 and day == 29 and not calendar.isleap(year):
            return f"{year} is not a leap year; February 29 is invalid."

        # General calendar validity
        try:
            datetime(year, month, day)
        except ValueError:
            # Handles invalid dates like 2024-02-30, 2024-13-01, etc.
            return "Invalid calendar date (e.g., February 30 doesn't exist)."
        return None

    def ValidateExpenseData(self, date_str: str, amount_str: str) -> Optional[str]:
        """
        - Category/Description are optional (handled elsewhere); we only validate date and amount here.
        - Returns None if valid; otherwise returns error message.
        """
        # Date checks
        date_error = self._ValidateDateStrict(date_str)
        if date_error:
            return date_error

        # Amount checks
        if not amount_str:
            return "Amount is required."
        try:
            amount_value = float(amount_str)
            if amount_value < 0:
                return "Amount cannot be negative."
        except ValueError:
            return "Amount must be a valid number."
        return None

    # --- CRUD ---
    def AddExpenseInteractive(self) -> None:
        print("Add a new expense:")
        date_str = input("Date (YYYY-MM-DD): ").strip()
        category = input("Category (optional): ").strip()
        amount_str = input("Amount: ").strip()
        description = input("Description (optional): ").strip()

        error = self.ValidateExpenseData(date_str, amount_str)
        if error:
            # Cancel this operation and return to main menu gracefully
            print(f"Error: {error}Returning to main menu without adding an expense.")
            return

        amount_value = float(amount_str)
        expense = Expense(
            date=date_str,
            category=(category or ""),  # store empty if skipped
            amount=amount_value,
            description=(description or ""),  # store empty if skipped
        )
        self.expenses.append(expense)
        print("Expense added successfully.")

    def ViewExpenses(self) -> None:
        if not self.expenses:
            print("No expenses to show.")
            return
        print("Your Expenses:")
        for idx, exp in enumerate(self.expenses, start=1):
            # Validate core fields before display
            err = self.ValidateExpenseData(exp.date, str(exp.amount))
            if err:
                print(f"Skipping invalid entry #{idx}: {err}")
                continue
            cat = exp.category if (exp.category and exp.category.strip()) else "(none)"
            desc = exp.description if (exp.description and exp.description.strip()) else "(none)"
            print(f"{idx}. {exp.date} | {cat} | ${float(exp.amount):.2f} | {desc}")

    def DeleteExpense(self) -> None:
        # Always show current list before prompting
        if not self.expenses:
            print("No expenses to delete.")
            return

        # Explicitly print current expenses here so the flow always starts with the list
        print("\nCurrent Expenses:")
        for idx, exp in enumerate(self.expenses, start=1):
            # Reuse display formatting but inline to avoid extra headers
            err = self.ValidateExpenseData(exp.date, str(exp.amount))
            if err:
                print(f"Skipping invalid entry #{idx}: {err}")
                continue
            cat = exp.category if (exp.category and exp.category.strip()) else "(none)"
            desc = exp.description if (exp.description and exp.description.strip()) else "(none)"
            print(f"{idx}. {exp.date} | {cat} | ${float(exp.amount):.2f} | {desc}")

        try:
            index_str = input("\nEnter the expense number to delete: ").strip()
            index = int(index_str)
            if index < 1 or index > len(self.expenses):
                print("Invalid number. Returning to main menu.")
                return
            removed = self.expenses.pop(index - 1)
            cat = removed.category or "(none)"
            desc = removed.description or "(none)"
            print(f"Deleted: {removed.date} | {cat} | ${float(removed.amount):.2f} | {desc}")
        except ValueError:
            print("Please enter a valid integer. Returning to main menu.")

    # --- Import / Merge ---
    def ImportExpensesFromCsv(self) -> None:
        path = input("Enter path to CSV file to import/merge: ").strip()
        if not path:
            print("No path provided. Returning to main menu.")
            return
        imported = self.storage.LoadExpensesFromCsv(path)
        if not imported:
            print("No expenses found to import or file could not be read.")
            return
        before = len(self.expenses)
        existing_keys = {e.ToKey() for e in self.expenses}
        added = 0
        for e in imported:
            if e.ToKey() not in existing_keys:
                self.expenses.append(e)
                existing_keys.add(e.ToKey())
                added += 1
        print(f"Imported {len(imported)} from file, added {added} new (deduplicated). Total is now {len(self.expenses)}.")

    # --- Calculations & Reports ---
    def CalculateTotalExpenses(self) -> float:
        total = 0.0
        for exp in self.expenses:
            try:
                total += float(exp.amount)
            except (TypeError, ValueError):
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
            key = (exp.category or "").strip() or "Uncategorized"
            category_totals[key] = category_totals.get(key, 0.0) + amt

        print("Expenses by Category:")
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
        print("Welcome to Personal Expense Tracker!")
        self.RunInteractiveMenu()

    def ShowMenu(self) -> None:
        print("Menu:")
        print("1) Add Expense")
        print("2) View Expenses")
        print("3) Delete Expense")
        print("4) Set Monthly Budget")
        print("5) Track Budget (Calculate Total & Compare)")
        print("6) Show Category Report")
        print("7) Save Expenses")
        print("8) Import/Merge CSV")
        print("9) Exit (Auto-Save)")

    def RunInteractiveMenu(self) -> None:
        while True:
            self.ShowMenu()
            choice = input("Choose an option (1-9): ").strip()
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
                self.tracker.ImportExpensesFromCsv()
            elif choice == "9":
                # Auto-save before exit
                self.tracker.SaveExpenses()
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please choose 1-9.")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    app = ExpenseApp()
    app.Start()

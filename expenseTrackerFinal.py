import csv, json, os
from datetime import datetime


#Expense Object
class Expense:
    def __init__(self, date, category, amount, description):
        self.date = date
        self.category = category
        self.amount = amount
        self.description = description

    def toDict(self):   # convert to dict (for CSV)
        return {
            'date': self.date,
            'category': self.category,
            'amount': "{:.2f}".format(self.amount),
            'description': self.description
        }

    # make an Expense object back from the csv file
    def fromDict(d):
        if not d: #bad data check
            return None   
        return Expense(
            d.get('date',''),
            d.get('category',''),
            float(d.get('amount',0.0)),
            d.get('description','')
        )
    
#File work: Save & Load
class ExpenseStorage:
    #save CSV file path
    def __init__(self, filePath='expenses.csv'):
        self.filePath = filePath

    #Save All Expenses to CSV
    def saveToCsv(self, allSpends):
        try:
            with open(self.filePath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date','category','amount','description'])
                writer.writeheader() #Making it header row
                for e in allSpends:
                    writer.writerow(e.toDict())
            print(f"✅ Saved {len(allSpends)} expenses to {self.filePath}")
        except OSError as err:
            print(f"⚠️ Problem saving: {err}")

    def loadFromCsv(self):
        data = []
        #Missing File Check
        if not os.path.exists(self.filePath):
            return data
        try:
            with open(self.filePath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f) #Using DictReader to read rows as dicts
                for r in reader:
                    try:
                        ex = Expense.fromDict(r)
                        if ex: 
                            data.append(ex) #Only adding valid expenses
                    except:
                        print(f"Skipping bad row: {r}")
                        continue
        except Exception as oops:
            print(f"Couldn’t load CSV: {oops}")
        return data

# Budget Manager
class BudgetManager:
    #Not hard coding budget since hardcoding it would mean it would reset every time the program ended.
    #Using Json file to store it just to mess with json.
    def __init__(self, budgetFile='budget.json'):
        self.budgetFile = budgetFile
        self.monthlyBudget = 0.0

    def loadBudget(self):
        #CHeck if file exists
        if not os.path.exists(self.budgetFile):
            return
        try:
            with open(self.budgetFile,'r',encoding='utf-8') as f:
                info = json.load(f)
                self.monthlyBudget = float(info.get('monthly_budget',0))
        except Exception as e:
            print(f"couldn’t read budget file: {e}")

    def saveBudget(self):
        try:
            with open(self.budgetFile,'w',encoding='utf-8') as f:
                json.dump({'monthly_budget': self.monthlyBudget}, f)
        except OSError as e:
            print(f"saveBudget failed: {e}")

    def setBudget(self):
        #Keep asking until valid input
        while True:
            val = input("\nEnter your monthly budget: ")
            try:
                amt = float(val)
                if amt < 0:
                    print("no negative numbers please.")
                    continue
                self.monthlyBudget = amt
                self.saveBudget()
                print("Budget set to $%.2f" % amt)
                break
            except ValueError:
                print("That wasn’t a number.")
            except OSError as e:
                print(f"saveBudget failed: {e}")

    def track(self, total):
        if self.monthlyBudget <= 0:
            print("You haven’t set a budget yet.")
            return
        remaining = self.monthlyBudget - total
        print(f"\nYour total spent: {total:.2f}")
        print(f"Budget: {self.monthlyBudget:.2f}")
        if remaining < 0:
            print(f"💸❗Over budget by {abs(remaining):.2f}")
        else:
            print(f"💸You still have {remaining:.2f} left.")

#Expense Tracker
class ExpenseTracker:
    def __init__(self, storage, budgetMgr):
        self.storage = storage
        self.budgetMgr = budgetMgr
        self.expenses = []

    #Validation
    def validateDate(self):
        while True:
            d = input("Date (YYYY-MM-DD or 'q' to cancel): ").strip()
            if d.lower() == 'q':
                return None
            try:
                datetime.strptime(d, "%Y-%m-%d")
                return d
            except ValueError:
                print("⚠️ Invalid date format. Please use YYYY-MM-DD (2025-10-28).")
    #Validation
    def validateAmount(self):
        while True:
            a = input("Amount (enter 'q' to cancel): ").strip()
            if a.lower() == 'q':
                return None
            try:
                val = float(a)
                if val < 0:
                    print("⚠️ Amount cannot be negative.")
                    continue
                return val
            except ValueError:
                print("⚠️ Please enter a valid number (25.50).")

    #Call Expense Addition
    def addExpense(self):
        print("\nAdd a new expense:")
        d = self.validateDate()
        if d is None:
            print("Returning to main menu.")
            return

        c = input("Category (optional): ").strip() #avoid unnecessary bugs
        a = self.validateAmount()
        if a is None:
            print("Returning to main menu.")
            return

        desc = input("Description (optional): ").strip()

        ex = Expense(d, c, a, desc)
        self.expenses.append(ex)
        print("✅ Expense added successfully!")

    def viewExpenses(self):
        if not self.expenses:
            print("No expenses yet.")
            return
        print("\n---Total Expenses---")
        i = 1 #reset
        for e in self.expenses:
            print(f"{i}) {e.date} | {e.category} | ${e.amount:.2f} | {e.description}")
            i+=1

    def deleteExpense(self):
        if not self.expenses:
            print("nothing to delete.")
            return
        while True:
            self.viewExpenses()
            choice = input("\nWhich expense would you like to delete ('q' to cancel): ").strip()
            if choice.lower() == 'q':
                return
            try:
                indexx = int(choice)
                if indexx <= 0 or indexx > len(self.expenses):
                    print("Out of range!")
                    continue
                dltd = self.expenses.pop(indexx-1)
                print("Removed:", dltd.category or "(none)", dltd.date, dltd.amount)
                return
            except ValueError:
                print("That wasn’t a number")

    def totalEx(self):
        total = sum(e.amount for e in self.expenses)
        return total

    def showByCategory(self):
        if not self.expenses:
            print("nothing recorded yet.")
            return
        sCategories = {}
        for e in self.expenses:
            if e.category:
                cat = e.category.strip() 
            else:
                cat = "Uncategorized"
            sCategories.setdefault(cat, 0.0) #Make Category 0 from start
            sCategories[cat] += float(e.amount)   # or simply: += e.amount

        print("\n---Expenses by Category---")
        for k in sorted(sCategories.keys()):
            print("-", k, ":", "$%.2f" % sCategories[k])

    def saveCurrent(self):
        self.storage.saveToCsv(self.expenses)

    def loadCurrent(self):
        self.expenses = self.storage.loadFromCsv()

#Main
class ExpenseApp:
    def __init__(self):
        self.store = ExpenseStorage()
        self.myBudgetStuff = BudgetManager()
        self.tracker = ExpenseTracker(self.store, self.myBudgetStuff)

    def start(self):
        self.tracker.loadCurrent()
        self.myBudgetStuff.loadBudget()
        print("\n---Expense Tracker App---")
        self.menuLoop()

    def menuLoop(self):
        while True:
            print("\nMenu:")
            print("1) Add Expense")
            print("2) View Expenses")
            print("3) Delete Expense")
            print("4) Set Budget")
            print("5) Track Budget")
            print("6) Category Report")
            print("7) Save")
            print("8) Exit")
            opt = input("Choose: ").strip()

            if opt=='1': 
                self.tracker.addExpense()
            elif opt=='2': 
                self.tracker.viewExpenses()
            elif opt=='3': 
                self.tracker.deleteExpense()
            elif opt=='4': 
                self.myBudgetStuff.setBudget()
            elif opt=='5':
                t = self.tracker.totalEx()
                self.myBudgetStuff.track(t)
            elif opt=='6': 
                self.tracker.showByCategory()
            elif opt=='7': 
                self.tracker.saveCurrent()
            elif opt=='8':
                self.tracker.saveCurrent()
                print("Bye 👋")
                break
            else:
                print("Try 1-8 please.")

if __name__ == "__main__":
    app = ExpenseApp()
    app.start()
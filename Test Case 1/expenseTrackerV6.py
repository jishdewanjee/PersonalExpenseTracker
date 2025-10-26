import csv, json, os
from datetime import datetime

# -------------------------------
# Expense "thingy" - one record
# -------------------------------
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
    
# -------------------------------------
# File work: Save & Load
# -------------------------------------
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
            print("✅ Saved", len(allSpends), "expenses to", self.filePath)
        except Exception as err:
            print("⚠️ Problem saving:", err)

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
                        print("Skipping bad row:", r)
                        continue
        except Exception as oops:
            print("Couldn’t load CSV:", oops)
        return data

# -------------------------------------
# Budget Manager
# -------------------------------------
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
            print("couldn’t read budget file:", e)

    def saveBudget(self):
        try:
            with open(self.budgetFile,'w',encoding='utf-8') as f:
                json.dump({'monthly_budget': self.monthlyBudget}, f)
        except Exception as e:
            print("saveBudget failed:", e)

    def setBudget(self):
        #Keep asking until valid input
        while True:
            val = input("Enter your monthly budget: ")
            try:
                amt = float(val)
                if amt < 0:
                    print("no negative numbers please.")
                    continue
                self.monthlyBudget = amt
                self.saveBudget()
                print("Budget set to $%.2f" % amt)
                break
            except:
                print("that’s not a valid number... try again")

    def track(self, total):
        if self.monthlyBudget <= 0:
            print("You haven’t set a budget yet.")
            return
        remaining = self.monthlyBudget - total
        print("Your total spent:", round(total,2))
        print("Budget:", round(self.monthlyBudget,2))
        if remaining < 0:
            print("💸 Over budget by", abs(remaining))
        else:
            print("You still have", remaining, "left.")

# -------------------------------------
# Expense Tracker
# -------------------------------------
class ExpenseTracker:
    def __init__(self, storage, budgetMgr):
        self.storage = storage
        self.budgetMgr = budgetMgr
        self.expenses = []

    def validateStuff(self, dateStr, cat, amtStr, desc):
        if not dateStr or not amtStr:
            return "Missing required info!"
        try:
            datetime.strptime(dateStr, "%Y-%m-%d")
        except:
            return "Date must be like 2025-10-20"
        try:
            amt = float(amtStr)
            if amt < 0: return "negative amount not allowed"
        except:
            return "Amount must be number"
        return None

    def addExpense(self):
        print("\nAdd a new expense:")
        d = input("Date (YYYY-MM-DD): ")
        c = input("Category: ")
        a = input("Amount: ")
        desc = input("Description: ")

        err = self.validateStuff(d,c,a,desc)
        if err:
            print("Error:", err)
            return

        ex = Expense(d,c,float(a),desc)
        self.expenses.append(ex)
        print("✅ added!")

    def viewAll(self):
        if not self.expenses:
            print("No expenses yet.")
            return
        print("\n--- All Expenses ---")
        i = 1
        for e in self.expenses:
            print(f"{i}) {e.date} | {e.category} | ${e.amount:.2f} | {e.description}")
            i+=1

    def deleteExpense(self):
        if len(self.expenses)==0:
            print("nothing to delete.")
            return
        self.viewAll()
        choice = input("Which one to delete?: ")
        try:
            idx = int(choice)
            if idx<=0 or idx>len(self.expenses):
                print("Out of range!")
                return
            gone = self.expenses.pop(idx-1)
            print("Removed:", gone.category, gone.amount)
        except:
            print("That wasn’t a number")

    def totalUp(self):
        total = 0
        for e in self.expenses:
            try:
                total += float(e.amount)
            except:
                pass
        return total

    def showByCategory(self):
        if not self.expenses:
            print("nothing recorded yet.")
            return
        cats = {}
        for e in self.expenses:
            cat = e.category.strip() if e.category else "Uncategorized"
            if cat not in cats:
                cats[cat] = 0
            try:
                cats[cat]+= float(e.amount)
            except:
                continue
        print("\nExpenses by Category:")
        for k in sorted(cats.keys()):
            print("-", k, ":", "$%.2f" % cats[k])

    def saveAll(self):
        self.storage.saveToCsv(self.expenses)

    def loadAll(self):
        self.expenses = self.storage.loadFromCsv()

# -------------------------------------
# Main App
# -------------------------------------
class ExpenseApp:
    def __init__(self):
        self.store = ExpenseStorage()
        self.myBudgetStuff = BudgetManager()
        self.tracker = ExpenseTracker(self.store, self.myBudgetStuff)

    def start(self):
        self.tracker.loadAll()
        self.myBudgetStuff.loadBudget()
        print("Welcome to the Expense Tracker thing!\n")
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
                self.tracker.viewAll()
            elif opt=='3': 
                self.tracker.deleteExpense()
            elif opt=='4': 
                self.myBudgetStuff.setBudget()
            elif opt=='5':
                tot = self.tracker.totalUp()
                self.myBudgetStuff.track(tot)
            elif opt=='6': 
                self.tracker.showByCategory()
            elif opt=='7': 
                self.tracker.saveAll()
            elif opt=='8':
                self.tracker.saveAll()
                print("Bye 👋")
                break
            else:
                print("Try 1-8 please.")

if __name__ == "__main__":
    app = ExpenseApp()
    app.start()
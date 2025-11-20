# Personal Expense Tracker 💰
A simple Python program (and Jupyter Notebook) to record, categorize, and analyze expenses - now with a **Web UI**!

This project was part of my course assignment where I learned to work with Object-Oriented Programming, file handling, and data persistence in Python.
I first started it as a standalone `.py` script, but later converted everything into Jupyter Notebook format to make it more organized and easier to explain what I learned along the way.

**NEW**: Now includes a modern web-based UI built with Streamlit for a better user experience!

## 📘 Overview
A simple Python program (and Jupyter Notebook) that records, categorizes, and analyzes expenses while keeping track of a monthly budget.  
The goal was to build something functional while also exploring concepts like validation, data saving/loading, and clean program structure.

## 🧩 Features
- **Web UI Interface** – Modern, intuitive Streamlit-based web interface
- **Dashboard** – Visual overview of expenses, budget, and spending trends
- Add, view, and delete expenses
- Category-wise totals with visual charts
- Monthly budget tracking with progress indicators
- Input validation for dates and amounts
- CSV + JSON storage for data persistence
- Error handling for invalid or missing data  

## 🧠 Tech Stack
- Python 3.x
- **Streamlit** – Web UI framework
- CSV, JSON – Data storage
- datetime – Date validation  

## 🚀 How to Run

### 🌐 Option 1 – Web UI (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`

### 🖥️ Option 2 – Run as a Python CLI file
```bash
python expenseTrackerFinal.py
```

### 📓 Option 3 – Jupyter notebook
Open `expenseTrackerFinal.ipynb` and run all cells.

## 📂 Files
- `app.py` – Streamlit web UI application
- `expenseTrackerFinal.py` – full CLI version (core logic)
- `expenseTrackerFinal.ipynb` – notebook version with markdown reflections
- `expenses.csv` / `budget.json` – auto-generated data files
- `README.md` – project overview
- `requirements.txt` – dependencies
- `.gitignore` – files to ignore in GitHub

```bash
✅ Saved 5 expenses to expenses.csv
💸 Total spent this month: $734.50
💰 Remaining budget: $1265.50
```

## 🤝 Contributing

We welcome contributions of all kinds — bug fixes, feature enhancements, refactoring, or documentation improvements.

To get started:
1. Fork the repo
2. Clone your fork: `git clone https://github.com/your-username/PersonalExpenseTracker.git`
3. Create a new branch: `git checkout -b feature-name`
4. Make your changes and commit: `git commit -m "Add feature"`
5. Push to your fork: `git push origin feature-name`
6. Open a Pull Request

Check out [`CONTRIBUTING.md`](CONTRIBUTING.md) for more details.

---

**.gitignore**
Prevents unwanted clutter in your repo:
Python

pycache/
*.pyc
*.pyo
*.pyd

Jupyter
.ipynb_checkpoints/

Data files (auto-generated)
expenses.csv
budget.json

Environments
.venv/
env/

---

Generate automatically:
```bash
pip freeze > requirements.txt
```

## LICENSE
For open source sharing, use MIT License:
MIT License
Copyright (c) 2025 [Debaditya Dewanjee]
Permission is hereby granted, free of charge, to any person obtaining a copy...

## Reflections
This project was actually really fun to work on. I spent a lot of time going over the notes again and again just to really understand how everything connects. Since I already had some background in OOP, I decided to take that route and picked the first project because it felt really comfortable. I’m hoping to give Project 2 a shot later on. I’m not the biggest fan of dealing with file saving and loading, so I kept the file names hardcoded and just played around with CSV and JSON instead. At first, I thought about hardcoding the budget too, but then I realized it wouldn’t make sense when loading old expense files with their own budgets. So I used a JSON file for that instead. I even tried storing the budget inside the CSV file, but that got messy real fast. My favorite parts were adding expenses and calculating totals or categories. I really enjoyed seeing the results through the CSV. The file management part was the hardest and honestly the most frustrating, but I learned a lot from it. I also had fun writing the user prompts and tried to think of every way Andrew might try to break the program. Ultimately it was a great experience and I learned how important it is to initialize things properly from the start to avoid weird bugs later on.

## ✅ Final File Tree
```bash
PersonalExpenseTracker/
├── app.py                      # Streamlit web UI
├── expenseTrackerFinal.py      # CLI version
├── expenseTrackerFinal.ipynb   # Jupyter notebook
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── .gitignore
├── LICENSE.md
└── (auto-generated)
    ├── expenses.csv
    └── budget.json
```

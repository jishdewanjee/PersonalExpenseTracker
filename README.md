# Personal Expense Tracker 💰
A simple Python program (and Jupyter Notebook) to record, categorize, and analyze expenses.

This project was part of my course assignment where I learned to work with Object-Oriented Programming, file handling, and data persistence in Python.  
I first started it as a standalone `.py` script, but later converted everything into Jupyter Notebook format to make it more organized and easier to explain what I learned along the way.

## 📘 Overview
A simple Python program (and Jupyter Notebook) that records, categorizes, and analyzes expenses while keeping track of a monthly budget.  
The goal was to build something functional while also exploring concepts like validation, data saving/loading, and clean program structure.

## 🧩 Features
- Add, view, and delete expenses  
- Category-wise totals  
- Monthly budget tracking  
- Input validation for dates and amounts  
- CSV + JSON storage  
- Error handling for invalid or missing data  

## 🧠 Tech Stack
- Python 3.x  
- CSV, JSON  
- datetime  

## 🚀 How to Run

### 🖥️ Option 1 – Run as a Python file
```bash
python expenseTrackerFinal.py
```
---
### Option 2 – Jupyter notebook
Open expenseTrackerFinal.ipynb and run all cells.

📂 Files
expenseTrackerFinal.py – full CLI version
expenseTrackerFinal.ipynb – notebook version with markdown reflections
expenses.csv / budget.json – auto-generated data files
README.md – project overview
requirements.txt – dependencies (optional)
.gitignore – files to ignore in GitHub

✅ Saved 5 expenses to expenses.csv
💸 Total spent this month: $734.50
💰 Remaining budget: $1265.50

🙌 Acknowledgments
Grateful for the feedback and guidance from my instructors and peers!

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

LICENSE
For open source sharing, use MIT License:
MIT License
Copyright (c) 2025 [Debaditya Dewanjee]
Permission is hereby granted, free of charge, to any person obtaining a copy...

Reflections
This project was actually really fun to work on. I spent a lot of time going over the notes again and again just to really understand how everything connects. Since I already had some background in OOP, I decided to take that route and picked the first project because it felt really comfortable. I’m hoping to give Project 2 a shot later on. I’m not the biggest fan of dealing with file saving and loading, so I kept the file names hardcoded and just played around with CSV and JSON instead. At first, I thought about hardcoding the budget too, but then I realized it wouldn’t make sense when loading old expense files with their own budgets. So I used a JSON file for that instead. I even tried storing the budget inside the CSV file, but that got messy real fast. My favorite parts were adding expenses and calculating totals or categories. I really enjoyed seeing the results through the CSV. The file management part was the hardest and honestly the most frustrating, but I learned a lot from it. I also had fun writing the user prompts and tried to think of every way Andrew might try to break the program. Ultimately it was a great experience and I learned how important it is to initialize things properly from the start to avoid weird bugs later on.

✅ Suggested Final File Tree
ExpenseTracker/
├── expenseTrackerFinal.py
├── expenseTrackerFinal.ipynb
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
└── (auto-generated)
    ├── expenses.csv
    └── budget.json

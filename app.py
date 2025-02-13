from flask import Flask, render_template, request, redirect, url_for, flash
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

class FinanceManager:
    def __init__(self, data_file="data.csv", budget_file="budget.csv"):
        self.data_file = data_file
        self.budget_file = budget_file

    def add_transaction(self, type, amount, category, description):
        with open(self.data_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([type, amount, category, datetime.now().strftime("%Y-%m-%d"), description])
    
    def view_summary(self):
        income, expenses = 0, 0
        category_expense = {}
        
        with open(self.data_file, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == "Income":
                    income += float(row[1])
                else:
                    expenses += float(row[1])
                    category_expense[row[2]] = category_expense.get(row[2], 0) + float(row[1])
        
        return income, expenses, category_expense

    def set_budget(self, category, amount):
        budgets = {}
        with open(self.budget_file, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                budgets[row[0]] = row[1]

        budgets[category] = amount
        with open(self.budget_file, "w", newline="") as file:
            writer = csv.writer(file)
            for cat, amt in budgets.items():
                writer.writerow([cat, amt])

    def check_budget_status(self):
        expenses = {}
        with open(self.data_file, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == "Expense":
                    expenses[row[2]] = expenses.get(row[2], 0) + float(row[1])

        budgets = {}
        with open(self.budget_file, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                budgets[row[0]] = float(row[1])

        exceeded_budgets = []
        for category, spent in expenses.items():
            if category in budgets and spent > budgets[category]:
                exceeded_budgets.append((category, spent, budgets[category]))
        
        return exceeded_budgets

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/add', methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        type = request.form["type"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        
        manager = FinanceManager()
        manager.add_transaction(type, amount, category, description)
        flash("Transaction added successfully!", "success")
        return redirect(url_for("home"))
    
    return render_template("add_transaction.html")

@app.route('/summary')
def summary():
    manager = FinanceManager()
    income, expenses, category_expense = manager.view_summary()
    return render_template("summary.html", income=income, expenses=expenses, category_expense=category_expense)

@app.route('/set_budget', methods=["GET", "POST"])
def set_budget():
    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        
        manager = FinanceManager()
        manager.set_budget(category, amount)
        flash("Budget set successfully!", "success")
        return redirect(url_for("home"))
    
    return render_template("set_budget.html")

@app.route('/check_budget')
def check_budget():
    manager = FinanceManager()
    exceeded_budgets = manager.check_budget_status()
    return render_template("budget_status.html", exceeded_budgets=exceeded_budgets)

if __name__ == "__main__":
    app.run(debug=True)

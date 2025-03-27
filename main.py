import pandas as pd
import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
from tabulate import tabulate


class CSVManager:
    CSV_FILE = "finance_data.csv"
    BACKUP_FILE = "finance_data_backup.csv"
    COLUMNS = ["Date", "Amount", "Category", "Description"]
    DATE_FORMAT = "%d-%m-%Y"

    @classmethod
    def _create_backup(cls):
        # Create a backup of the data file
        if os.path.exists(cls.CSV_FILE):
            df = pd.read_csv(cls.CSV_FILE)
            df.to_csv(cls.BACKUP_FILE, index=False)

    @classmethod
    def _validate_datafile(cls):
        # Check if data file is valid and readable
        try:
            df = pd.read_csv(cls.CSV_FILE)
            if not all(col in df.columns for col in cls.COLUMNS):
                raise ValueError("Invalid columns in data file")
            pd.to_datetime(df["Date"], format=cls.DATE_FORMAT)
            df["Amount"] = pd.to_numeric(df["Amount"])
            return True
        except Exception as e:
            print(f"⚠️ Error: Data file is corrupted! {str(e)}")
            if os.path.exists(cls.BACKUP_FILE):
                print("🔄 Attempting to restore from backup...")
                os.replace(cls.BACKUP_FILE, cls.CSV_FILE)
                return cls._validate_datafile()
            return False

    @classmethod
    def initialize(cls):
        # Initialize or validate data file
        try:
            if not os.path.exists(cls.CSV_FILE):
                pd.DataFrame(columns=cls.COLUMNS).to_csv(cls.CSV_FILE, index=False)
                return True
            return cls._validate_datafile()
        except Exception as e:
            print(f"⚠️ Critical error initializing data file: {str(e)}")
            return False

    @classmethod
    def add_entry(cls, date, amount, category, description):
        # Add a new transaction entry
        cls._create_backup()
        new_entry = {
            "Date": date,
            "Amount": amount,
            "Category": category,
            "Description": description
        }
        try:
            with open(cls.CSV_FILE, "a", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
                writer.writerow(new_entry)
            print("✅ Entry added successfully")
            return True
        except Exception as e:
            print(f"⚠️ Failed to add entry: {str(e)}")
            return False

    @classmethod
    def _display_transactions(cls, df, title="Transactions"):
        # Helper function to display transactions in a table format
        if df.empty:
            print("ℹ️ No transactions found")
            return
        
        df["Date"] = pd.to_datetime(df["Date"], format=cls.DATE_FORMAT)
        df = df.sort_values("Date", ascending=False)
        
        print(f"\n📊 {title}")
        print(tabulate(
            df.assign(Date=df["Date"].dt.strftime(cls.DATE_FORMAT)),
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
            floatfmt=".2f"
        ))
        
        # Display summary statistics
        total_income = df[df["Category"] == "Income"]["Amount"].sum()
        total_expense = df[df["Category"] == "Expense"]["Amount"].sum()
        print(f"\n💵 Total Income: ${total_income:,.2f}")
        print(f"💸 Total Expense: ${total_expense:,.2f}")
        print(f"💰 Net Savings: ${(total_income - total_expense):,.2f}")

    @classmethod
    def get_transactions(cls, start_date=None, end_date=None):
        # Get transactions with optional date filtering
        try:
            df = pd.read_csv(cls.CSV_FILE)
            df["Date"] = pd.to_datetime(df["Date"], format=cls.DATE_FORMAT)
            
            if start_date and end_date:
                start = datetime.strptime(start_date, cls.DATE_FORMAT)
                end = datetime.strptime(end_date, cls.DATE_FORMAT)
                mask = (df["Date"] >= start) & (df["Date"] <= end)
                df = df.loc[mask]
                title = f"Transactions from {start_date} to {end_date}"
            else:
                title = "All Transactions"
            
            cls._display_transactions(df, title)
            return df
        except Exception as e:
            print(f"⚠️ Error reading transactions: {str(e)}")
            return pd.DataFrame()

    @classmethod
    def get_monthly_summary(cls):
        # Generate monthly summary report
        try:
            df = pd.read_csv(cls.CSV_FILE)
            df["Date"] = pd.to_datetime(df["Date"], format=cls.DATE_FORMAT)
            df["Month"] = df["Date"].dt.to_period("M")
            
            summary = df.groupby(["Month", "Category"]).sum(numeric_only=True).unstack()
            summary.columns = summary.columns.droplevel()
            summary = summary.fillna(0)
            summary["Net"] = summary.get("Income", 0) - summary.get("Expense", 0)
            
            print("\n📅 Monthly Summary")
            print(tabulate(
                summary.reset_index().assign(Month=lambda x: x["Month"].astype(str)),
                headers=["Month", "Income", "Expense", "Net Savings"],
                tablefmt="fancy_grid",
                floatfmt=".2f",
                showindex=False
            ))
            return summary
        except Exception as e:
            print(f"⚠️ Error generating monthly summary: {str(e)}")
            return pd.DataFrame()

def clear_screen():
    # Clear the terminal screen
    os.system("cls" if os.name == "nt" else "clear")

def press_enter_to_continue():
    # Wait for user to press Enter
    input("\nPress Enter to continue...")

def add_transaction():
    # Handle transaction addition flow
    clear_screen()
    print("➕ Add New Transaction\n")
    date = get_date("Enter date (dd-mm-yyyy) or leave blank for today: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    while category is None:
        category = get_category()
    description = get_description()
    if CSVManager.add_entry(date, amount, category, description):
        press_enter_to_continue()

# def plot_transactions(df):
#     df.set_index("Date", inplace = True)
#     income_df = (
#                 df[df["Category"] == "Income"]
#                 .resample("D")
#                 .sum()
#                 .reindex(df.index,fill_value = 0)
#     )
#     expense_df = (
#                 df[df["Category"] == "Expense"]
#                 .resample("D")
#                 .sum()
#                 .reindex(df.index,fill_value = 0)
#     )
#     plt.figure(figsize=(10,5))
#     plt.plot(income_df.index,income_df["Amount"], label="Income", color="g")
#     plt.plot(expense_df.index,expense_df["Amount"], label="Expense",color="r")
#     plt.xlabel("Date")
#     plt.ylabel("Amount")
#     plt.title("Income and Expenses")
#     plt.legend()
#     plt.grid(True)
#     plt.show()

def view_transactions():
    # Handle transaction viewing flow
    clear_screen()
    print("🔍 View Transactions\n")
    print("1. View all transactions")
    print("2. View by date range")
    print("3. Monthly summary")
    choice = input("\nChoose an option: ")
    
    if choice == "1":
        clear_screen()
        CSVManager.get_transactions()
    elif choice == "2":
        clear_screen()
        print("📅 Enter date range")
        start_date = get_date("Start date (dd-mm-yyyy): ")
        end_date = get_date("End date (dd-mm-yyyy): ")
        CSVManager.get_transactions(start_date, end_date)
    elif choice == "3":
        clear_screen()
        CSVManager.get_monthly_summary()
    else:
        print("⚠️ Invalid option")
    
    press_enter_to_continue()

def main_menu():
    # Display main menu and handle user input
    while True:
        clear_screen()
        print("💰 Personal Finance Manager\n")
        print("1. Add Transaction")
        print("2. View Transactions & Reports")
        print("3. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice, please try again")
            press_enter_to_continue()

if __name__ == "__main__":
    if CSVManager.initialize():
        main_menu()
    else:
        print("⚠️ Critical error: Unable to initialize application")
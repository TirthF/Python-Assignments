"""
Transaction CSV Processor Implementation
"""
#It will create 3 files credit.csv , debit.csv , error.csv

import csv
import os
from datetime import datetime
from collections import defaultdict
 
def get_file_path():
    """Helper function to get a valid file path from the user."""
    while True:
        file_path = input("Enter the path to the transactions CSV file: ").strip()
        if not file_path:
            print("Error: File path cannot be empty.")
            continue
        if not os.path.isfile(file_path):
            print("Error: File does not exist. Please try again.")
            continue
        return file_path

def main():
    file_path = get_file_path()

    balances = defaultdict(float)
    errors = []
    credits = []
    debits = []

    # 1. Read and process the input CSV
    try:
        with open(file_path, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, start=1):
                try:
                    # Validate required keys exist
                    if not all(k in row for k in ("tid", "acc", "type", "amount", "time")):
                        raise ValueError("Missing required columns in CSV row")

                    tid = row["tid"]
                    acc = row["acc"]
                    transaction_type = row["type"].upper()
                    
                    try:
                        amount = float(row["amount"])
                    except ValueError:
                        raise ValueError("Amount must be a numeric value")
                        
                    timestamp = row["time"]

                    if not tid or not acc:
                        raise ValueError("Missing transaction or account ID")

                    if transaction_type not in ("CREDIT", "DEBIT"):
                        raise ValueError("Invalid transaction type")

                    if amount <= 0:
                        raise ValueError("Amount must be greater than 0")

                    # Validate timestamp format
                    datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

                    # Apply transaction
                    if transaction_type == "CREDIT":
                        credits.append(row)
                        balances[acc] += amount
                    else:
                        debits.append(row)
                        balances[acc] -= amount

                except Exception as e:
                    row["reason"] = str(e)
                    errors.append(row)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 2. Write processed data to output files
    try:
        with open("credit.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["tid", "acc", "type", "amount", "time"])
            writer.writeheader()
            writer.writerows(credits)

        with open("debit.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["tid", "acc", "type", "amount", "time"])
            writer.writeheader()
            writer.writerows(debits)

        with open("error.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["tid", "acc", "type", "amount", "time", "reason"])
            writer.writeheader()
            writer.writerows(errors)
    except IOError as e:
        print(f"Error writing output files: {e}")
        return

    # 3. Calculate and display final balances
    result = sorted(balances.items(), key=lambda x: (-abs(x[1]), x[0]))

    print("\n--- Final Balances ---")
    for account, balance in result:
        if balance.is_integer():
            balance = int(balance)
        print(account, balance)

    print("\nFiles created: credit.csv, debit.csv, error.csv")

if __name__ == "__main__":
    main()
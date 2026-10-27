"""
Banking System with Batch Transactions Implementation
"""
class InsufficientBalanceError(Exception):
    pass

class AccountNotFoundError(Exception):
    pass

class Account:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self._balance = balance
        self._history = []

    @property
    def balance(self):
        return self._balance

    @property
    def history(self):
        return self._history.copy()

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Invalid amount")

        self._balance += amount
        self._history.append(("DEPOSIT", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Invalid amount")

        if amount > self._balance:
            raise InsufficientBalanceError("Insufficient balance")

        self._balance -= amount
        self._history.append(("WITHDRAW", amount))


class Transaction:
    def __init__(self, operation, account_from=None, account_to=None, amount=0):
        self.operation = operation
        self.account_from = account_from
        self.account_to = account_to
        self.amount = amount


class Bank:
    def __init__(self):
        self.accounts = {}
        self.batch_number = 0
        self.failed_batches = []

    def add_account(self, account_id, balance):
        self.accounts[account_id] = Account(account_id, balance)

    def get_account(self, account_id):
        if account_id not in self.accounts:
            raise AccountNotFoundError("Account not found")
        return self.accounts[account_id]

    def deposit(self, account_id, amount):
        self.get_account(account_id).deposit(amount)

    def withdraw(self, account_id, amount):
        self.get_account(account_id).withdraw(amount)

    def transfer(self, from_id, to_id, amount):
        sender = self.get_account(from_id)
        receiver = self.get_account(to_id)

        sender.withdraw(amount)
        receiver.deposit(amount)

    def execute(self, operation):
        parts = operation.split()
        if not parts:
            return

        if parts[0] == "DEPOSIT":
            self.deposit(parts[1], int(parts[2]))

        elif parts[0] == "WITHDRAW":
            self.withdraw(parts[1], int(parts[2]))

        elif parts[0] == "TRANSFER":
            self.transfer(parts[1], parts[2], int(parts[3]))

    def execute_batch(self, operations):
        self.batch_number += 1

        old_balances = {
            account_id: account.balance
            for account_id, account in self.accounts.items()
        }

        old_history = {
            account_id: account.history
            for account_id, account in self.accounts.items()
        }

        try:
            for operation in operations:
                self.execute(operation)

        except Exception:
            for account_id, account in self.accounts.items():
                account._balance = old_balances[account_id]
                account._history = old_history[account_id]

            self.failed_batches.append(self.batch_number)
            print(f"FAILED {self.batch_number}")


def get_integer_input(prompt):
    """Helper function to get a valid integer."""
    while True:
        try:
            val = int(input(prompt))
            if val < 0:
                print("Error: Value cannot be negative.")
                continue
            return val
        except ValueError:
            print("Error: Please enter a valid integer.")

def main():
    bank = Bank()

    # 1. Setup initial accounts
    n = get_integer_input("Enter the number of initial accounts: ")

    if n > 0:
        print(f"Please enter {n} lines of <account_id> <balance>:")

    for i in range(n):
        while True:
            try:
                line = input(f"Account {i+1}: ").strip()
                account_id, balance = line.split()
                bank.add_account(account_id, int(balance))
                break
            except ValueError:
                print("Error: Please provide exactly two space-separated values: <account_id> <balance_integer>")

    # 2. Execute operations
    q = get_integer_input("\nEnter the number of operations to execute: ")

    batch_operations = []
    in_batch = False

    if q > 0:
        print(f"Please enter {q} operations:")

    for i in range(q):
        operation = input(f"Op {i+1}: ").strip()

        if operation == "BATCH_BEGIN":
            in_batch = True
            batch_operations = []

        elif operation == "BATCH_END":
            bank.execute_batch(batch_operations)
            in_batch = False

        elif in_batch:
            batch_operations.append(operation)

        else:
            try:
                bank.execute(operation)
            except Exception:
                pass

    # 3. Print final account balances
    print("\n--- Final Balances ---")
    for account_id in sorted(bank.accounts):
        print(account_id, bank.accounts[account_id].balance)


if __name__ == "__main__":
    main()
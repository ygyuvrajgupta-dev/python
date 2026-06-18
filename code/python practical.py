# design a class bank account with:
# deposit()
# withdrawl()
# balence()
# raise exception for insufficient balence
class InsufficientBalanceError(Exception):
    """Custom exception for insufficient balance in the account."""
    pass


class BankAccount:
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self._balance = initial_balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount
        print(f"Deposited: {amount}. New balance: {self._balance}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self._balance:
            raise InsufficientBalanceError(
                f"Insufficient balance! Tried to withdraw {amount}, "
                f"but only {self._balance} available."
            )
        self._balance -= amount
        print(f"Withdrew: {amount}. New balance: {self._balance}")

    def balance(self):
        return self._balance


# Example usage:
try:
    account = BankAccount("Yuvraj", 1000)
    account.deposit(500)
    account.withdraw(200)
    print("Final Balance:", account.balance())
    account.withdraw(2000)  # This will raise InsufficientBalanceError
except InsufficientBalanceError as e:
    print("Error:", e)



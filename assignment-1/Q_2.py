"""
Password Strength Checker Implementation
"""
import re

def get_banned_words(b):
    """Helper function to securely get banned words list."""
    banned = []
    if b > 0:
        print(f"Please enter {b} banned words:")
    for i in range(b):
        word = input(f"Banned word {i+1}: ").strip().lower()
        banned.append(word)
    return banned

def main():
    # 1. Get the number of banned words
    while True:
        try:
            b = int(input("Enter the number of banned words: "))
            if b < 0:
                print("Error: Number cannot be negative.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid integer.")

    banned_words = get_banned_words(b)

    # 2. Get the number of passwords to check
    while True:
        try:
            n = int(input("Enter the number of passwords to check: "))
            if n < 0:
                print("Error: Number cannot be negative.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid integer.")

    # 3. Check each password
    if n > 0:
        print(f"\nPlease enter the {n} passwords:")
        
    for i in range(1, n + 1):
        password = input(f"Password {i}: ").strip()

        # Check for weak length
        if len(password) < 6 or len(password) > 12:
            print(f"{i}: WEAK_LENGTH")
            continue

        # Check for weak pattern (missing character classes)
        lower = re.search(r"[a-z]", password)
        upper = re.search(r"[A-Z]", password)
        digit = re.search(r"\d", password)
        special = re.search(r"[$#@]", password)

        if not (lower and upper and digit and special):
            print(f"{i}: WEAK_PATTERN")
            continue

        # Check if compromised
        password_lower = password.lower()
        compromised = False
        for word in banned_words:
            if word in password_lower:
                compromised = True
                break

        if compromised:
            print(f"{i}: COMPROMISED")
            continue

        # Check for repeating characters (3 or more)
        if re.search(r"(.)\1\1\1", password):
            print(f"{i}: WEAK_PATTERN")
            continue

        print(f"{i}: STRONG")

if __name__ == "__main__":
    main()
"""
Interactive Calculator Implementation
"""
class InvalidFormatError(Exception):
    pass

class UnknownVariableError(Exception):
    pass

class DivisionByZeroError(Exception):
    pass

class UnsupportedOperatorError(Exception):
    pass


variables = {}

def get_value(value):
    """Retrieves variable value or parses numeric literal."""
    if value in variables:
        return variables[value]

    try:
        return float(value)
    except ValueError:
        raise UnknownVariableError("Unknown variable")


def calculate(left, operator, right):
    """Performs the arithmetic calculation."""
    a = get_value(left)
    b = get_value(right)

    if operator not in ['+', '-', '*', '/', '%']:
        raise UnsupportedOperatorError("Unsupported operator")

    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        if b == 0:
            raise DivisionByZeroError("Division by zero")
        return a / b
    elif operator == '%':
        if b == 0:
            raise DivisionByZeroError("Division by zero")
        return a % b

def main():
    print("Welcome to Interactive Calculator.")
    print("Commands:")
    print("  x = 5 (assign variable)")
    print("  x + 3 (evaluate formula)")
    print("  quit  (exit)")
    
    while True:
        line = input("\n> ").strip()

        if line.lower() == "quit":
            break
            
        if not line:
            continue

        try:
            if '=' in line:
                # Variable assignment
                parts = line.split('=')

                if len(parts) != 2:
                    raise InvalidFormatError("Invalid assignment format")

                name = parts[0].strip()
                value = parts[1].strip()

                if not name.isidentifier():
                    raise InvalidFormatError("Invalid variable name")

                variables[name] = get_value(value)

            else:
                # Formula evaluation
                parts = line.split()

                if len(parts) != 3:
                    raise InvalidFormatError("Invalid formula format")

                result = calculate(parts[0], parts[1], parts[2])

                if result.is_integer():
                    print(int(result))
                else:
                    print(result)

        except InvalidFormatError as e:
            print("InvalidFormatError")
        except UnknownVariableError as e:
            print("UnknownVariableError")
        except DivisionByZeroError as e:
            print("DivisionByZeroError")
        except UnsupportedOperatorError as e:
            print("UnsupportedOperatorError")

if __name__ == "__main__":
    main()
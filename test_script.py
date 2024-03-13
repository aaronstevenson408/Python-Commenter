import random  # Import the random module

"""
This is a sample Python script for testing the code parsing and documentation generation.
"""

global_variable = True  # Define a global variable
taxidermy = True  # Define a global variable

class MyClass:
    """
    A simple class with a method.
    """
    def __init__(self, value):
        self.value = value

    def double(self):
        return self.value * 2

    def triple(self):  # Nested function within MyClass
        return self.value * 3


def add_numbers(a, b):
    """
    Add two numbers and return the result.
    """
    return a + b

def multiply_numbers(a, b):
    result = a * b  # Multiply the numbers
    return result

def main():
    x = 5
    y = 3

    # Nested function within main()
    def generate_random_number():
        """
        Generate a random number using random.randint().
        """
        return random.randint(1, 10)

    random_number = generate_random_number()
    print(f"Random number between 1 and 10: {random_number}")

    sum_result = add_numbers(x, y)
    print(f"The sum of {x} and {y} is {sum_result}")

    obj = MyClass(10)
    doubled_value = obj.double()
    print(f"The doubled value is {doubled_value}")

    tripled_value = obj.triple()
    print(f"The tripled value is {tripled_value}")

    product = multiply_numbers(x, y)
    print(f"The product of {x} and {y} is {product}")


if __name__ == "__main__":
    main()

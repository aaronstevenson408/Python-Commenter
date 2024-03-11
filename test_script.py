# test_script.py

"""
This is a sample Python script for testing the code parsing and documentation generation.
"""

class MyClass:
    """
    A simple class with a method.
    """
    def __init__(self, value):
        self.value = value

    def double(self):
        return self.value * 2


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
    sum_result = add_numbers(x, y)
    print(f"The sum of {x} and {y} is {sum_result}")

    obj = MyClass(10)
    doubled_value = obj.double()
    print(f"The doubled value is {doubled_value}")

    product = multiply_numbers(x, y)
    print(f"The product of {x} and {y} is {product}")


if __name__ == "__main__":
    main()
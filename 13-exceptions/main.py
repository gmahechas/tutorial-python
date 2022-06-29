from CustomError import CustomError

result = None

try:
    x = 10
    y = 10

    if x == y:
        raise CustomError("x is equal to y")
    result = x / y
except ZeroDivisionError as exception:
    print("ZeroDivisionError:", exception)
except TypeError as exception:
    print(f"TypeError: {exception}")
except Exception as exception:
    print(f"Exception: {exception}")
else:
    print(f"all OK")
finally:
    print(f"finally")  # always executed

print(f"Result: {result}")

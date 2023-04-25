try:
    a = 10
    b = 0

    print(a / b)
except (ZeroDivisionError, TypeError) as error:
    print("Error")
    print(type(error))
    print(error)

finally:
    print("Finally")

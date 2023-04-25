try:
    age = 2
    if age < 10:
        raise Exception("Age cannot be negative less than 10", 25, "other string")

except Exception as exception:
    print(exception)

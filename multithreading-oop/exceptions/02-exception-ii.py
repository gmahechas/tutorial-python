while True:
    try:
        result = input("Enter a number:")
        result = int(result)
        break
    except ValueError:
        print("Invalid input")

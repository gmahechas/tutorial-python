def main():
    # if
    number: int = 3
    if number > 5:
        print("condition was true")
    elif number == 5:
        print("condition was true")
    else:
        print("condition was false")

    # ternary
    result: int = 7 if number > 5 else 2
    print(result)

    # while
    condition: int = 1
    while condition <= 5:
        print(condition)
        condition += 1

    # for
    for i in range(1, 6):
      print(i)

	# list comprehension
    numbers = [1, 2, 3, 4, 5]
    squares = [number ** 2 for number in numbers]
    print(squares)


if __name__ == "__main__":
    main()

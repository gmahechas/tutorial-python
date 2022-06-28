def factorial_recursive(n):
    if n == 0:
        return 1
    else:
        return n * factorial_recursive(n-1)


print(factorial_recursive(5))


def my_recursive(n):
    if n >= 1:
        print(n)
        my_recursive(n-1)
    elif n == 0:
        return
    else:
        print("Error")


my_recursive(3)

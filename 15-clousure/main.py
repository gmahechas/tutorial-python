def operation1(x, y):
    def add():
        return x + y

    return add


my_func1 = operation1(10, 20)
print(my_func1())


def operation2(x, y):
    def add():
        return x + y

    def sub():
        return x - y

    return add, sub


my_function = operation2(10, 20)
print(my_function[1]())


# lambda
def operation3(x, y):
    return lambda: x + y


print(operation3(15, 20)())

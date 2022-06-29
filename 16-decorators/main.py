def decorator_func1(func):
    def wrapper_func():
        print("wrapper executed this before {}".format(func.__name__))
        func()
        print("wrapper executed this after {}".format(func.__name__))

    return wrapper_func


def decorator_func2(func):
    def wrapper_func(*args, **kwargs):
        print("wrapper executed this before {}".format(func.__name__))
        func(*args, **kwargs)
        print("wrapper executed this after {}".format(func.__name__))

    return wrapper_func


@decorator_func1
def show_message1():
    print("Hello World")


show_message1()

print("\n")


@decorator_func2
def show_message2(message):
    print(message)


show_message2("this is the message")

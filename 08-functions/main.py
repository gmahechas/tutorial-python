def my_function_with_args(*args):
    for name in args:
        print("Hello, " + name)


my_function_with_args("John", "Jane", "Mary")


def my_function_with_kwargs(**kwargs):
    for key, value in kwargs.items():
        print("%s is %s" % (key, value))


my_function_with_kwargs(name="John", age=30, city="New York")

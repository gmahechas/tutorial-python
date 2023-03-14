my_lambda_function = lambda x, y: x + y
print(my_lambda_function(4, 3))

my_lambda_function2 = lambda: 3 + 5
print(my_lambda_function2())

my_lambda_function3 = lambda x=7, y=9: x + y
print(my_lambda_function3())

my_lambda_function4 = lambda *args, **kwargs: len(args) + len(kwargs)
print(my_lambda_function4(1, 3, a=1, b=2))

my_lambda_function5 = lambda x: x
x = list(map(my_lambda_function5, 'hello'))
print(x)

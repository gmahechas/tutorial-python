def multiply(*args):
    total = 0
    for arg in args:
        total += arg
    return total


result = multiply(1, 3, 5)
print(result)



def named(**kwargs):
	print(kwargs)


dic = {'name': 'jesus', 'age': 777}
result2 = named(**dic)
print(result2)

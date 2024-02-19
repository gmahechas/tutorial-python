# example of shadowing

x = 10
z = 7

def my_func() -> None:
	""" if x is shadowed it will not work"""
	x = z + 20
	print(x)

my_func()

print(x)
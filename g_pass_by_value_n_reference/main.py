def main():
	"""
		pass by reference apply only for mtable objects (Lists, Dictionaries, Sets)
		it does not apply for Numbers Strings Tuples
	"""
	pass_by_value()
	print("#######")
	pass_by_reference()

def pass_by_value():
	x = 10
	print(f"The initial value of x is: {x}")
	pass_by_value_one(x) # this does not change the value of x, you have to do x = pass_by_value_one(x)
	print(f"The final value of x is: {x}")

def pass_by_value_one(x: int):
	x = x + 1
	print(f"The value of x in the inner scope is: {x}")

def pass_by_reference():
	x = dict({"a": 1, "b": 2})
	print(f"The initial value of x is: {x}")
	pass_by_reference_one(x)
	print(f"The final value of x is: {x}")

def pass_by_reference_one(x: dict):
	x["a"] = x["a"] + 1
	print(f"The value of x in the inner scope is: {x}")

if __name__ == "__main__":
	main()
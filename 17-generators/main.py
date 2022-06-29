def generator():
    yield 1
    yield 2
    yield 3


gen = generator()
print(next(gen))
print(next(gen))
print(next(gen))
# print(next(gen))  # error


# generations expressions
multi = (x * 2 for x in range(3))
print(next(multi))  # 0
print(next(multi))  # 2
print(next(multi))  # 4


# with list
my_list = ["a", "b", "c"]
generator2 = (x for x in my_list)
print(next(generator2))  # a
print(next(generator2))  # b
print(next(generator2))  # c

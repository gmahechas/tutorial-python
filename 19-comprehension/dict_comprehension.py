dict1 = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

x = dict1.keys()
print(x)

y = dict1.values()
print(y)

z = dict1.items()
print(z)

new_dict = {k: v * 2 for (k, v) in dict1.items()}
print(new_dict)

new_dict_keys = {k * 2: v for (k, v) in dict1.items()}
print(new_dict_keys)

# add item in dictonary

dict2 = {i: i ** 2 for i in range(10) if i % 2 == 0}
print(dict2)

# using lambda function
feh = {'temp1': 10, 'temp2': 20, 'temp3': 30, 'temp4': 40}
the_func = lambda fa_temp: (float(5) / 9) * (fa_temp - 32)
the_map = list(map(the_func, feh.values()))
the_dict = dict(zip(feh.keys(), the_map))

print(the_dict)

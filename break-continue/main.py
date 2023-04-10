
my_range = range(0, 10, 1)
print(list(my_range))

for number in my_range:
    if number == 5:
        continue

    print(number)

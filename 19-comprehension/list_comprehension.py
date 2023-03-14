numbers = [1, 2, 3, 4, 5]
squares = []

for n in numbers:
    squares.append(n ** 2)

print(squares)

# using comprehension
new_squares = [n ** 2 for n in numbers]

print(new_squares)

# using comprehension 2
list1 = [1, 2, 3, 4, 5]
list2 = [1, 3, 4, 5, 6]

intersection = [x for x in list1 for y in list2 if x == y]
intersection2 = [(x, y) for x in list1 for y in list2 if x != y]
print(intersection)
print(intersection2)

# using comprehension 3
list3 = ['Hello World']
list4 = [my_string.lower() for my_string in list3]
print(list4)

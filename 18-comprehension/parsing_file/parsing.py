op = open('python.txt', 'r')

output = [row for row in op if "comprehensions" in row]
print(output)

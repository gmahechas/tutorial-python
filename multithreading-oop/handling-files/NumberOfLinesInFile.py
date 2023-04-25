file = open('test-file.txt', 'r')

line_counter = 0

for line in file:
    line_counter += 1

file.close()

print(f"number of lines is {line_counter}")
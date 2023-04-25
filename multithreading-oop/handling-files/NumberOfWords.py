file = open('test-file.txt', 'r')

words_counter = 0

for line in file:
    words = line.split()
    words_counter += len(words)

file.close()

print(f"number of lines is {words_counter}")
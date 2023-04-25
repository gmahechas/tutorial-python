file = open('test-file.txt', 'r')

counter = 0
for line in file:
    words = line.split()
    counter += len([word for word in words if word.lower() == 'is'])

file.close()
print(counter)

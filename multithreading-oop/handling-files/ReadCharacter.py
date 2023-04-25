file = open('test-file.txt', 'r')

while True:

    current_char = file.read(4)
    if not current_char:
        break

    print(current_char)

file.close()

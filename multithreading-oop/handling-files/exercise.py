file = open('input_file.txt', 'r')
output = open('output_file.txt', 'a')

sentence = ''

for index, line in enumerate(reversed(list(file))):
    sentence += line[::-1]
    sentence += '\n'

file.close()

output.write(sentence)
output.close()

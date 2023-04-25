# try:
#     file = open("input_file", "r")
#
# except FileExistsError as error:
#     print('This is an error')
#
# finally:
#     file.close()

try:
    with open("../handling-files/test-files.txt", "r") as file:
        for line in file:
            print(line)
except FileNotFoundError as error:
    print(error)

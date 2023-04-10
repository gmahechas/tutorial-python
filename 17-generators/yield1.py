# def producer():
#     for num in range(10):
#         print(num)
#
#
# producer()


def producer():
    for value in range(10):
        if value % 2 == 0:
            yield value


for num in producer():
    print(num)

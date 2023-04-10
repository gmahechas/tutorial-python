def show_name(*args):
    print(type(args))  # tuple

    # for index in range(len(names)):
    #     print(names[index])

    for arg in args:
        print(arg)


show_name('Gustavo', 'Alexandra', 'Isabella')


def show_name_2(**kwargs):
    print(type(kwargs))  # dict
    print(kwargs['name'])


show_name_2(name='gustavo', lastname='mache', age=36)

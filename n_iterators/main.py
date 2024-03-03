class Counter():
    __count: int
    __max: int

    def __init__(self, max: int = 10):
        self.__count = 0
        self.__max = max
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.__count < self.__max:
            self.__count += 1
            return self.__count
        else:
            raise StopIteration

    # Context manager, to able use with
    def __enter__(self):
        self.__count = 0  # Inicializar o resetear el contador
        return self  # Retorna la instancia para ser usada dentro del contexto with

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Aquí podrías limpiar recursos si es necesario

def main():
    # arrays, accepts duplicates
    my_array: list[int] = [1, 2, 3, 3]
    for number in my_array:
        print(number)

    # tuples, accepts duplicates
    my_tuple: tuple[int] = (4, 5, 6)
    for number in my_tuple:
        print(number)

    # sets, does not accept duplicates
    my_set: set[int] = {7, 8, 9, 8}
    for number in my_set:
        print(number)

    # dictionaries
    my_dic: dict[str, int] = {"a": 10, "b": 11, "c": 12}
    for key, value in my_dic.items():
        print(key, value)

    # iter
    my_array2: list[int] = [13, 14, 15, 16]
    my_iter = iter(my_array2)
    print(next(my_iter))
    print(next(my_iter))
    print(next(my_iter))
    print(next(my_iter))

    # generators
    for number in generador_numeros():
        print(number)

    # counter
    print("Counter")
    counter = Counter()
    for number in counter:
        print(number)

    print("With")
    with Counter(5) as counter:
        for number in counter:
            print(number)


def generador_numeros():
    for i in range(5):
        yield i

if __name__ == "__main__":
    main()

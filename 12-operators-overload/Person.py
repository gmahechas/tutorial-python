class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __add__(self, other):
        return f"{self.name} {other.name}"

    def __sub__(self, other):
        return f"{self.age-other.age}"


if __name__ == "__main__":
    person1 = Person("John", 30)
    person2 = Person("Doe", 25)
    print(person1 + person2)
    print(person1 - person2)

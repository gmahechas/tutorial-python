class Person:
    def __init__(self, name, age):
        self.name = name
        self._age = age  # private attribute

    def __str__(self):
        return f"{self.name} is {self._age} years old."


person1 = Person("John", 30)
print(person1)
person1._age = 35  # but this should not be allowed
print(person1)


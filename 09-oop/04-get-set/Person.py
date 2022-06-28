class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age

    @property  # with this we do not need () after the method
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @name.deleter
    def name(self):
        del self._name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, age):
        self._age = age

    @age.deleter
    def age(self):
        del self._age

    def __str__(self):
        return f"{self._name} is {self._age} years old."

    def __del__(self):
        print(f"{self._name} is dead.")


person1 = Person("John", 30)
print(person1)

person1.name = "John Doe"
print(person1)

del person1


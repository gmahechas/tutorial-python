class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def show_detail(self):
        print(f"{self.name} is {self.age} years old.")

    def __str__(self):
        return f"{self.name} is {self.age} years old."


person1 = Person("John", 30)
print(person1)
person1.name = "Jane"
print(person1)

person2 = Person("Dane", 30)
Person.show_detail(person2)

person2.phone = "123-456-7890"  # others object can not access this attribute
print(person2.phone)

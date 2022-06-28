from Person import Person


class Employee(Person):

    def __init__(self, name, age, salary):
        super().__init__(name, age)
        self._salary = salary

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, salary):
        self._salary = salary

    @salary.deleter
    def salary(self):
        del self._salary

    def __str__(self):
        return f"{super().__str__()} and earns {self._salary}."


employee1 = Employee("John", 30, 1000)
print(employee1)

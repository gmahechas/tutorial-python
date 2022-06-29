from Employee import Employee
from Manager import Manager


def print_details(obj):
    print(obj)
    print(type(obj))
    if isinstance(obj, Manager):
        print(obj.department)


employee1 = Employee('John', '$100')
print_details(employee1)


manager1 = Manager('Alice', '$200', 'IT')
print_details(manager1)

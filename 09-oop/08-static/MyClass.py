class MyClass:
    class_var = "Hello"

    def __init__(self, instance_var):
        self.instance_var = instance_var

    @classmethod
    def class_method(cls):
        print(cls.class_var)

    @staticmethod
    def static_method():
        print(MyClass.class_var)

    def instance_method(self):
        print("#############################")
        print(self.instance_var)
        print(self.class_var)
        print(MyClass.class_var)
        print("#############################")


# access class variables
print(MyClass.class_var)

# also access instance variables
my_class1 = MyClass("World")
print(my_class1.class_var)
print(my_class1.instance_var)

# add a new class variable
MyClass.class_var2 = "Goodbye"  # Static variable on fly

# access class variables
my_class2 = MyClass("Python")
print(my_class2.class_var)
print(my_class2.instance_var)


# access class methods
MyClass.class_method()

# access class methods through instance
my_class3 = MyClass("Python")
my_class3.class_method()
my_class3.instance_method();

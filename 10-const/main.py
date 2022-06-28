MY_CONST = "Hello"  # This is a constant and cannot be changed


class Math:
    PI = 3.141592653589793

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return self.PI * self.radius ** 2

    def circumference(self):
        return 2 * self.PI * self.radius

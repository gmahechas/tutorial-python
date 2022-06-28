from Figure import Figure
from Color import Color


class Square(Figure, Color):
    def __init__(self, width, height, color):
        Figure.__init__(self, width, height)
        Color.__init__(self, color)

    def area(self):
        return self.width * self.height

    def __str__(self):
        return "Square: width = {}, height = {}, area = {}".format(self.width, self.height, self.area())


if __name__ == "__main__":
    square1 = Square(10, 20, "red")
    print(square1)
    print(Square.mro())  # print method resolution order

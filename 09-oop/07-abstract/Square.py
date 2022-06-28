from Figure import Figure


class Square(Figure):

    def __init__(self, width, height):
        super().__init__(width, height)

    def area(self):
        return self.width * self.height


if __name__ == "__main__":
    square1 = Square(10, 10)
    print(square1.area())

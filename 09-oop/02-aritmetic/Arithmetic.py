class Arithmetic:
    """
    Arithmetic class
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def sum(self):
        return self.a + self.b

    def sub(self):
        return self.a - self.b

    def mul(self):
        return self.a * self.b

    def div(self):
        return self.a / self.b


arithmetic = Arithmetic(3, 5)
print(f"div is: {arithmetic.div():.2f}")

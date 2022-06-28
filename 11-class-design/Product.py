
class Product:

    product_counter = 0

    def __init__(self, product_name, product_price):
        Product.product_counter += 1
        self._product_id = Product.product_counter
        self._product_name = product_name
        self._product_price = product_price

    @property
    def product_price(self):
        return self._product_price

    def __str__(self):
        return f"Id:{self._product_id} Name:{self._product_name} Price:{self._product_price}"


if __name__ == "__main__":
    product1 = Product("Coffee", 1.50)
    product2 = Product("Tea", 2.00)
    print(product1)
    print(product2)

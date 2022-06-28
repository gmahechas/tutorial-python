from Product import Product


class Order:
    order_counter = 0

    def __init__(self, products: list[Product]):
        Order.order_counter += 1
        self.order_id = Order.order_counter
        self.products = products

    def add_product(self, product):
        self.products.append(product)

    def total_price(self):
        total = 0
        for product in self.products:
            total += product.product_price
        return total

    def __str__(self):
        products_str = "Products:\n"
        for product in self.products:
            products_str += f"{product.__str__()}\n"
        return f"########\nOrder id: {self.order_id}\n{products_str}"


if __name__ == "__main__":
    product1 = Product("Coffee", 1.50)
    product2 = Product("Tea", 2.00)
    order1 = Order([product1, product2])
    print(order1)
    print(f"Total: {order1.total_price()}")

    product3 = Product("CocaCola", 3.50)
    order1.add_product(product3)
    print(order1)
    print(f"Total: {order1.total_price()}\n########")


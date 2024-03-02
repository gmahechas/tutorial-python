from typing import Generic, TypeVar
T = TypeVar('T')

class Point(Generic[T]):
	__x: T
	__y: T

	def __init__(self, x: T, y: T):
		self.x = x
		self.y = y

	@property
	def x(self):
		return self.__x

	@x.setter
	def x(self, x):
		self.__x = x

	@property
	def y(self):
		return self.__y

	@y.setter
	def y(self, y):
		self.__y = y

def main():
	point_int = Point(1, 2)
	print(point_int.x, point_int.y)

	point_float = Point(1.1, 2.2)
	print(point_float.x, point_float.y)

	print(calculate_area(point_int))
	print(calculate_area(point_float))


def calculate_area(point: Point[T]) -> T:
	return point.x * point.y


if __name__ == "__main__":
	main()

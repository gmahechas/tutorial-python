from typing import Callable

def main():
	sum_func: Callable[[int, int], int] = lambda x, y: x + y
	print(sum_func(5, 2))


if __name__ == "__main__":
	main()
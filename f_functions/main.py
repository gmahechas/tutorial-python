def main() -> None:
	grettings_first_part = get_gretings_first("Hello")
	grettings_second_part = get_greetings_second("World")
	print(f"{grettings_first_part} {grettings_second_part}")

def get_gretings_first(grettings: str) -> str:
	return grettings

def get_greetings_second(grettings: str) -> str:
	return grettings


if __name__ == "__main__":
	main()
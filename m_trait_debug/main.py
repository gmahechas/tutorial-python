class User:
	__username: str
	__age: int

	def __init__(self, username: str, age: int) -> None:
		self.__username = username
		self.__age = age

	@property
	def username(self) -> str:
		return self.__username

	@username.setter
	def username(self, username: str) -> None:
		self.__username = username

	@property
	def age(self) -> int:
		return self.__age

	@age.setter
	def age(self, age: int) -> None:
		self.__age = age


	def __str__(self) -> str:
		return f"username: {self.username}, age: {self.age}"



def main():
	user = User("tavogus", 37)
	print(user)

	user.username = "analuna"
	user.age = 4
	print(user)

if __name__ == "__main__":
	main()
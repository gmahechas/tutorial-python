from enum import Enum

class Role(Enum):
	ADMIN = 'Admin'
	USER = 'User'

class User:

	__username: str | None = None
	__email: str | None = None
	__age: int | None = None
	__active: bool | None = None
	__rol: Role | None = None

	def __init__(self, username: str, email: str, age: int, active: bool, rol: Role):
		self.__username = username
		self.__email = email
		self.__age = age
		self.__active = active
		self.__rol = rol

	@property
	def username(self):
		return self.__username

	@username.setter
	def username(self, username):
		self.__username = username

 	# if I remove this __email will warn me
	@property
	def email(self):
		return self.__email

	@email.setter
	def email(self, email):
		self.__email = email

	def __str__(self):
		return f"username: {self.__username}, age: {self.__age}, email: {self.__email}, active: {self.__active}, rol: {self.__rol.value}"


from abc import ABC, abstractmethod
from typing import Protocol


# interfaces
class Speaks(ABC):
	@abstractmethod
	def speak(self) -> None:
		print("speak before")

class Fly(Protocol):
	def fly(self) -> None:
		print("I can not fly")
	
# classes
class Human(Speaks, Fly):
	def speak(self):
		print("Hello")

class Animal(Speaks, Fly):
	def speak(self):
		print("Woof")

	def fly(self):
		print("I can fly because I am an animal")

# duck typing
def speak(obj: Speaks):
	obj.speak()

def fly(obj: Fly):
	obj.fly()


def main():
	human = Human()
	animal = Animal()

	human.speak()
	animal.speak()

	speak(human)
	speak(animal)

	human.fly()
	animal.fly()

	fly(human)
	fly(animal)


if __name__ == "__main__":
	main()
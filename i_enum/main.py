from user.user import User, Role

def main():
		user1 = User("tavogus", "tavogus@me.com", 32, True, Role.ADMIN)
		print(user1)


if __name__ == '__main__':
	main()
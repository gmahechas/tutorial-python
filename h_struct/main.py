from user.user import User


def main():
		user1 = User("tavogus", "tavogus@me.com", 32, True)
		print(user1)
		new_email = user1.email
		print(f"The new email is: {new_email}")
		new_email = "analuna@me.com"
		print(f"The new email is: {new_email}")
    
		user1.email = new_email
		print(user1)
				
if __name__ == "__main__":
    main()

class UserSignUpDTO:

    email: str
    password: str

    def __init__(self, **kwargs):
        self.email = kwargs["email"]
        self.password = kwargs["password"]

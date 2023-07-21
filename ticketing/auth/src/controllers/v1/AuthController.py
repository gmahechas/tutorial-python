class AuthController:

    def __init__(self):
        print("AuthController initialized")

    def signup(self) -> str:
        return "signup"

    def signin(self) -> str:
        return "signin"

    def sign_out(self) -> str:
        return "sign_out"

    def current_user(self) -> str:
        return "current_user"

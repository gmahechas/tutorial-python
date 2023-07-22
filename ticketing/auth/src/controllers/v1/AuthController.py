from controllers.v1.UserSignUpDTO import UserSignUpDTO


class AuthController:

    def __init__(self):
        pass

    def signup(self, user_sign_up_dto: UserSignUpDTO) -> str:
        return "signup"

    def signin(self) -> str:
        return "signin"

    def sign_out(self) -> str:
        return "sign_out"

    def current_user(self) -> str:
        return "current_user"

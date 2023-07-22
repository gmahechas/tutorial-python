from flask import Blueprint, request
from controllers.v1.AuthController import AuthController
from controllers.v1.UserSignUpDTO import UserSignUpDTO
from utils.HttpMethods import HttpMethods
from utils.decorators import body

auth_blueprint = Blueprint('users', __name__, url_prefix='/users')

auth_controller = AuthController()


@auth_blueprint.route('/signup', methods=[HttpMethods.POST.value])
@body(UserSignUpDTO)
def signup(user_sign_up_dto: UserSignUpDTO):
    return auth_controller.signup(user_sign_up_dto)


@auth_blueprint.route('/signin', methods=[HttpMethods.POST.value])
def signin():
    return 'signin'


@auth_blueprint.route('/sign_out', methods=[HttpMethods.POST.value])
def sign_out():
    return 'sign_out'


@auth_blueprint.route('/current_user', methods=[HttpMethods.GET.value])
def current_user():
    return auth_controller.current_user()

from functools import wraps
from flask import request


# def body(_class):
#     def wrapper(_function):
#         def decorator():
#             instance = _class(**request.json)
#             return _function(instance)
#         return decorator
#     return wrapper


def body(_class):
    def wrapper(_function):
        @wraps(_function)
        def decorator():
            instance = _class(**request.json)
            return _function(instance)
        return decorator

    return wrapper


# def body(_class):
#     def wrapper(_function):
#         @wraps(_function)
#         def decorator(**kwargs):
#             # print(*args)
#             # instance = _class(**request.json)
#             return _function(*list(kwargs.values()))
#         return decorator
#
#     return wrapper
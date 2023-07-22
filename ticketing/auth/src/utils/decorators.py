from flask import request


def body(_class):
    def wrapper(_function):
        def decorator():
            instance = _class(**request.json)
            return _function(instance)
        return decorator
    return wrapper

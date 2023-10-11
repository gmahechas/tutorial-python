from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_user():
    user = dict({"name": "Ana", "age": 4})
    return Response(user)

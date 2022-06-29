class MyClass:
    def __init__(self, public, protected, private):
        self.public = public
        self._protected = protected
        self.__private = private


obg = MyClass('public', 'protected', 'private')
print(obg.public)
print(obg._protected)
print(obg.__private)  # error

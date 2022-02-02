# LEGB RULE
# L: local
# E: enclosing
# G: global
# B: built-in


# L: local
# def report():
#     x = 'inside'
#     return x
#
#
# print(report())


# E: enclosing
# x = 'THIS IS GLOBAL LEVEL'
#
#
# def enclosing():
#     x = 'enclosing level'
#
#     def inside():
#         print(x)
#     inside()
#
#
# enclosing()


# G: global
# x = 'THIS IS GLOBAL LEVEL'
#
#
# def enclosing():
#
#     def inside():
#         print(x)
#     inside()
#
#
# enclosing()

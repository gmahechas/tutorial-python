t = 5, 11
x, y = t
print(x)
print(y)


l = [1, 2, 3, 4, 5]
one, *rest = l
print(one)
print(rest)

l2 = [1, 2, 3, 4, 5]
*rest2, last = l
print(rest2)
print(last)


player_name, total_score, initial_socre = 'Guss', 100, 0
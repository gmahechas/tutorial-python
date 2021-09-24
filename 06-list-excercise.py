numbers = [1, 3, 5]
doubled = [num * 2 for num in numbers]

print(doubled)

friends = ['jesus', 'gustavo', 'alexandra']
starts_j = [friend for friend in friends if friend.startswith('j')]
print(starts_j)

""" pass by value """
friends2 = ['jesus', 'gustavo', 'alexandra']
friends3 = [*friends2]
friends3.append('analuna')
print(friends2)


test_set= {'foo': 'bar'}
""" test_set2 = test_set """
test_set2 = {**test_set}
test_set2['foo'] = 'barsito'
print(test_set)

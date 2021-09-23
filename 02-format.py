#%% 1 way
name = 'Gustavo'
grettings = f'Hello this is {name}'

print(grettings)

#%% 2 way
name2 = 'Analuna'
grettings2 = 'Hello I am {}'
with_name = grettings2.format(name2)
print(with_name)
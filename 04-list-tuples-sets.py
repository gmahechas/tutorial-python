# %% uses
list = ['jesus', 'gustavo', 'alexandra']
tuple = ('jesus', 'gustavo', 'alexandra')
set = {'jesus', 'gustavo', 'alexandra'}

# %%

friends = {'jesus', 'gustavo', 'alexandra'}
abroad = {'jesus', 'alexandra'}
local_friends = friends.difference(abroad)
print(local_friends)

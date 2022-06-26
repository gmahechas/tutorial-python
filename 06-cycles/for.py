my_str = "analuna"

for char in my_str:
    print(char)
    if char == "l":
        break
print("###############")
for char in my_str:
    if char == "l":
        continue
    print(char)

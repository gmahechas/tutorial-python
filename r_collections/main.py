from typing import Set

def main():
  array_1 = [1, 2]
  array_1.append(3)
  print(array_1)

  # hashset/set
  set_1: set[int] = {1, 2}
  set_1.add(3)
  print(set_1)
  
  # hashmap/dict
  dict_1: dict[str, int] = {"a": 1, "b": 2}
  dict_1["c"] = 3
  print(dict_1)
  
  

if __name__ == "__main__":
		main()
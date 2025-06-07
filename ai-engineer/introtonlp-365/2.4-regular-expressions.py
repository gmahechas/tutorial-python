import re

my_folder = r"desktop\notes\desktop\notes_two"
print("my_folder: ", my_folder)

""" Search for a pattern in a string """
result_search = re.search("desktop", my_folder)
print("result_search: ", result_search.group())

""" Replace a pattern in a string """
the_string = r"sara was able to help me find the items quickly"
the_new_string = re.sub("sara", "sarah", the_string)
print("the_new_string: ", the_new_string)

""" Search for a pattern in a list of strings """
customer_reviews = [
    "I love this product, it's amazing!",
    "This is the worst service I've ever had.",
    "I'm very happy with the purchase.",
    "I'm very unhappy with the purchase.",
    "sarah was able to help me find the items quickly",
    "amazing product, amazing service!",
]
sarah_reviews = []
pattern_to_find = r"sarah?"

for review in customer_reviews:
    if re.search(pattern_to_find, review):
        sarah_reviews.append(review)

print("sarah_reviews: ", sarah_reviews)

""" Search for a pattern at the beginning of a string """
a_reviews = []
pattern_to_find_for_a = r"^a"

for review in customer_reviews:
    if re.search(pattern_to_find_for_a, review):
        a_reviews.append(review)

print("a_reviews: ", a_reviews)

""" Search for a pattern at the end of a string """
z_reviews = []
pattern_to_find_for_z = r"y$"

for review in customer_reviews:
    if re.search(pattern_to_find_for_z, review):
        z_reviews.append(review)

print("z_reviews: ", z_reviews)




# Example of Loop in Python

# Write a short story of 3 lines
story = """Once upon a time there was a king. 
He had a queen and a son. 
He was a good king."""

words = story.split()


# 1. For Loop
# for word in words:
#     print(word)

# 2. While Loop
# i = 0
# while i < len(words):
#     print(words[i])
#     i = i + 1

# 3. Nested Loop
# for i in words:
#     for j in words:
#         print(i, j)


# 4. Infinite Loop
#while True:
#    print("Infinite Loop")


# 5. Break Statement
# for i in words:
#     if i == "queen":
#         break
#     print(i)

# 6. Continue Statement
#for i in words:
#    if i == "queen":
#        continue #Skip the queen
#    print(i)


# 7. Pass Statement
#for i in words:
#    if i == "queen":
#        pass #Do nothing
#    print(i)


# 8. Else Statement
#for i in words:
#    print(i)
#else:
#    print("Loop is finished")

# 9. Enumerate Function
for i, word in enumerate(words):
    print(i, word)

# 10. Zip Function
for i, word in zip(words, range(len(words))):
    print(i, word)


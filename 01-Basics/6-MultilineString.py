# Example of Multiline String in Python
story = """Once upon a time there was a king. 
He had a queen and a son. 
He was a good king."""
print(story)
print("\n")

print("Length of the story", len(story))
print("Number of times the word king appears", story.count("king"))
print("Number of times the word king appears", story.count("king"))
print("\n")

print("Replace king with SivaJi", story.replace("king", "SivaJi"))
story = story.replace("king", "SivaJi")
print(story.upper())

print("\n")
print(story.lower())

 


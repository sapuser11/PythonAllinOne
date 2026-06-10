## create multi-line string in python using triple quotes 
story = """Once there was a thirsty crow. It found a pot with little water. 
The crow dropped pebbles into the pot. Water rose up. 
The crow drank and flew away happily."""

print(f"length of story is {len(story)} characters")

print(f"the word crow is found at {story.find('crow')} @ character position")

print(f"the word crow is found at {story.index('crow')} @ character position")

##string is immutable, so we cannot change it directly
story = story.replace("crow", "raven")  # replace 'crow' with 'rave'

print(story)

#convert string to lower case
print(story.lower())
#convert string to upper case
print(story.upper())
#split string into list of words
words = story.split()
#print all words
for word in words:
    print(word)

#check if string starts with a word
print(story.startswith("Once"))
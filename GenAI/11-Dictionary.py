# Example of Dictionary

dictionary = {"name": "John", "age": 30, "city": "New York"}
print("Print Dictionary : ", dictionary)

# Add of dictionary
dictionary["gender"] = "Male"
print("Add of Dictionary : ", dictionary)

# Remove of dictionary
dictionary.pop("gender")
print("Remove of Dictionary : ", dictionary)

# Copy of dictionary
dictionary.copy()
print("Copy of Dictionary : ", dictionary)

# Clear of dictionary
dictionary.clear()
print("Clear of Dictionary : ", dictionary)

print(dictionary.keys())
print(dictionary.values())
print(dictionary.items())

print(dictionary.get("name"))
print(dictionary.get("age"))
print(dictionary.get("city"))
print(dictionary.get("gender"))

#print(dictionary.pop("name"))
#print(dictionary.pop("age"))
#print(dictionary.pop("city"))
#print(dictionary.pop("gender"))

print(dictionary.update({"name": "John", "age": 30, "city": "New York"}))

#print(dictionary.popitem())
#print(dictionary.popitem())
#print(dictionary.popitem())
#print(dictionary.popitem())




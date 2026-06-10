# List creation with text
my_list = ['apple', 'banana', 'cherry']
# List creation with numbers
my_numbers = [1, 2, 3, 4, 5]

# print first and last item of the list
print("First item:", my_list[0])
print("Last item:", my_list[-1])
#add an item to the list
my_list.append('mango')
#addd item in middle of the list
my_list.insert(2, 'orange')
print("Updated list:", my_list)
##extract data from the list
print("Extracted item:", my_list[1:-1])  # Extract items from index 1 to n-1st value
## count the number of items in the list
print("Number of items in the list:", len(my_list))
##remove an item from the list
my_list.remove('banana')
# remove the last item from the list
my_list.pop()

# list membership test
if 'apple' in my_list:
    print("'apple' is in the list")

# List concatenation
new_list = my_list + my_numbers 
print("Concatenated list:", new_list)

# List Comprehension
squared_numbers = [x**2 for x in my_numbers]
print("Squared numbers:", squared_numbers)


###Example of sets
# Sets are unordered collections of unique elements
# Example of creating a set
my_set = {1, 2, 3, 4, 5}
# Adding elements to a set
my_set.add(6)
# Removing elements from a set
my_set.remove(2)
# Checking membership in a set
if 3 in my_set:
    print("3 is in the set")
# Set operations
union_set = my_set.union({7, 8})
intersection_set = my_set.intersection({3, 4, 5})
# Printing the results
print("Union of sets:", union_set)
# Printing the intersection of sets
print("Intersection of sets:", intersection_set)


##Tuples
# Tuples are immutable sequences
# Example of creating a tuple
my_tuple = (1, 2, 3, 4, 5)
# Accessing elements in a tuple
print("First element of tuple:", my_tuple[0])
# Tuples can be unpacked
a, b, c = my_tuple[:3]
print("Unpacked values:", a, b, c)
# Example of a tuple with mixed data types
mixed_tuple = (1, "apple", 3.14, True)
# Accessing elements in a mixed tuple
print("Mixed tuple first element:", mixed_tuple[0])
# Example of a tuple with nested data structures
nested_tuple = (1, (2, 3), [4, 5])
# Accessing elements in a nested tuple
print("Nested tuple second element:", nested_tuple[1])
# Example of a tuple with a single element
single_element_tuple = (42,)
# Accessing the single element in a single-element tuple
print("Single element tuple:", single_element_tuple[0])


##Dictionaries
# Dictionaries are collections of key-value pairs like JSON objects
# Example of creating a dictionary of employee data
employee_data = {
    "name": "John Doe",
    "age": 30,
    "department": "Engineering",
    "skills": ["Python", "JavaScript", "C++"]
}

# Accessing values in a dictionary
print("Employee Name:", employee_data["name"])
# Using get method to access values
print("Employee Age:", employee_data.get("age", "Not specified"))
# Adding a new key-value pair to the dictionary
employee_data["salary"] = 60000
# Removing a key-value pair from the dictionary
employee_data.pop("department", None)
# Iterating over keys and values in a dictionary
for key, value in employee_data.items():
    print(f"{key}: {value}")

# Removing a key-value pair using del
del employee_data["skills"]  # Removing a key-value pair

# dictionary comprehension
squared_dict = {x: x**2 for x in range(5)}
print("Squared dictionary:", squared_dict)
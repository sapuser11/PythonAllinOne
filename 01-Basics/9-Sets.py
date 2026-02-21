# Sets DataType
# Key Features of Sets along with examples

#Sets always start with { } and end with { }
sets = {1, 2, 3, 4, 5, 6, 8, 7}
print("Print Sets : ", sets)

# Sets is a collection of unique items
#Example : sets = {1, 2, 3, 4, 5, 6, 8, 7}
sets2 = {1, 2, 3, 4, 4, 5, 6, 8, 7}
sets2.add(6)
print("Add + Duplicate Check in Sets : ", sets2) 

# Sets is unordered

# Sets is unindexed

# Sets is unchangeable
#sets.replace(6, 7)
#print("Replace Sets : ", sets) 

sets.pop()
print("Pop Sets : ", sets)


sets.copy()
print("Copy Sets : ", sets)

sets.clear()
print("Clear Sets : ", sets)


import math

a = 10
b = 25

addition = a + b
subtraction = b - a
multiplication = a * b
division = b / a
modulus = b % a
exponentiation = a ** 2

num = -7.65
rounded = round(num) # Rounds to the nearest integer
print(f"Rounded: {rounded}")
absolute_value = abs(num) # Returns the absolute value
print(f"Absolute value: {absolute_value}")
#smaller integer
celing = math.ceil(num) # Returns the smallest integer greater than or equal to num
print(f"Ceiling: {celing}")

##Logical Operators
is_equal = (a == b)  # False
is_not_equal = (a != b)  # True
is_greater = (a > b)  # False
is_less = (a < b)  # True
is_greater_equal = (a >= b)  # False
is_less_equal = (a <= b)  # True
is_true = True
is_false = False
is_and = is_true and is_false  # False
is_or = is_true or is_false  # True

##print all the results of logical operators
print(f"Is Equal: {is_equal}")
print(f"Is Not Equal: {is_not_equal}")
print(f"Is Greater: {is_greater}")
print(f"Is Less: {is_less}")
print(f"Is Greater or Equal: {is_greater_equal}")
print(f"Is Less or Equal: {is_less_equal}")
print(f"Is And: {is_and}")
print(f"Is Or: {is_or}")
#scalar variable - store single value

#string variable
from datetime import datetime


name = "Anubhav"

#integer variable
age = 30

#float variable
height = 5.9

#boolean variable
is_student = False

# Displaying the variables
print("Name: ", name, " is of type ", type(name))
print("Age: ", age, " is of type ", type(age))
print("Height: ", height, " is of type ", type(height))
print("Is Student: ", is_student, " is of type ", type(is_student))

#type conversion
age_str = "56"
print("Age as string: ", age_str, " is of type ", type(age_str))
age_int = int(age_str)  # Convert string to integer
print("Age as string: ", age_int, " is of type ", type(age_int))

##we can use float() to convert string to float
##we can use str() to convert integer or float to string

#simple if condition
newage = input("Enter your age: ")
if int(newage) > 18:
    print(name, "is an adult.")
    ##we can use 2 more ways to print string to user
    print(f"{name} with height {height} is an adult. {datetime.now()}")  # f-string, when we want to include variables in string
    print("Welcome to Anubhav Gen AI training!")
elif int(newage) == 18:
    print(name, "is just an adult.")
else:
    print(name, "is not an adult.")

# a function with args and kwargs
def dynamic_function(*args, **kwargs):
    print("Positional arguments:", args)
    print("Keyword arguments:", kwargs) 
    for arg in args:
        print("Processing positional argument:", arg)
    for key, value in kwargs.items():
        print(f"Processing keyword kwargs: {key} = {value}")


dynamic_function(1, 2, 3, name="Alice", age=30, city="New York")
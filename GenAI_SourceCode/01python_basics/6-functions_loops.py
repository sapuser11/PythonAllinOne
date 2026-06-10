

##from util import print_my_list_of_products, calculate_total_price, calculate_price_with_gst  
import util.reuse as util
        

##Create a list of dictionary with products and their prices with name, price, quantity, and category.
products = [
    {"name": "Apple", "price": 0.5, "quantity": 10, "category": "Fruit"},
    {"name": "Banana", "price": 0.3, "quantity": 20, "category": "Fruit"},
    {"name": "Carrot", "price": 0.2, "quantity": 15, "category": "Vegetable"},
    {"name": "Broccoli", "price": 0.4, "quantity": 5, "category": "Vegetable"},
    {"name": "Milk", "price": 1.0, "quantity": 10, "category": "Dairy"},
    {"name": "Cheese", "price": 2.5, "quantity": 5, "category": "Dairy"}
]
    

util.print_my_list_of_products(products)
print(util.calculate_total_price(products[0]))  # Output: 4.5 (0.5 * 10 * 0.9)
util.print_my_list_of_products(products)
print(util.calculate_price_with_gst(products[2]))  # Output: 5.04 (4.5 * 1.12 for Fruit)

##if you get the JSON data we can use the json module to convert it to a python object
import json
# Example JSON data
json_data =    '''
[
    {"name": "Apple", "price": 0.5, "quantity": 10, "category": "Fruit"},
    {"name": "Banana", "price": 0.3, "quantity": 20, "category": "Fruit"},
    {"name": "Carrot", "price": 0.2, "quantity": 15, "category": "Vegetable"},
    {"name": "Broccoli", "price": 0.4, "quantity": 5, "category": "Vegetable"},
    {"name": "Milk", "price": 1.0, "quantity": 10, "category": "Dairy"},
    {"name": "Cheese", "price": 2.5, "quantity":    5, "category": "Dairy"}
]'''
# Convert JSON data to Python object
products_from_json = json.loads(json_data)
util.print_my_list_of_products(products_from_json)
print(util.calculate_total_price(products_from_json[0]))  # Output: 4.5

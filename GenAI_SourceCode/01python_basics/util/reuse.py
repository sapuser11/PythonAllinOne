
##functions created using def keyword
def print_my_list_of_products(products):
    for product in products:
        print(f"Product: {product['name']}, Price: {product['price']}, Quantity: {product['quantity']}, Category: {product['category']}")

def calculate_total_price(product): 
    if product['category'] == 'Fruit':
        # return data in same directory 
        product['price'] = product['price'] * product['quantity'] * 0.9  # 10% discount for fruits
    elif product['category'] == 'Vegetable':
        product['price'] = product['price'] * product['quantity'] * 0.95  # 5% discount for vegetables
    else:
        product['price'] = product['price'] * product['quantity']
    return product

def calculate_price_with_gst(product):
        # Calculate base price after discount
        discounted_product = calculate_total_price(product.copy())
        base_price = discounted_product['price']
        # Apply GST based on category
        if product['category'] == 'Fruit':
            gst_rate = 0.12
        elif product['category'] == 'Dairy':
            gst_rate = 0.10
        elif product['category'] == 'Vegetable':
            gst_rate = 0.10
        else:
            gst_rate = 0.05
        total_price_with_gst = base_price * (1 + gst_rate)
        return total_price_with_gst


##this code is used when we want to test the functions in this file

if __name__ == "__main__":
    ##testing code to print a list of products with 3 products
    products = [
        {"name": "Apple", "price": 0.5, "quantity": 10, "category": "Fruit"},
        {"name": "Banana", "price": 0.3, "quantity": 20, "category": "Fruit"},
        {"name": "Carrot", "price": 0.2, "quantity": 15, "category": "Vegetable"}
    ]
    print_my_list_of_products(products)
    print(calculate_total_price(products[0]))  # Output: 4.5 (
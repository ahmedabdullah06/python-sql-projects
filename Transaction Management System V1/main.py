import os
import mysql.connector
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = mydb.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS products (product_id INT AUTO_INCREMENT PRIMARY KEY, item_name VARCHAR(255), rating INT, cost DECIMAL(10,2));")
cursor.execute("CREATE TABLE IF NOT EXISTS customer (user_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255) UNIQUE);")
cursor.execute("CREATE TABLE IF NOT EXISTS orders (order_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, order_date DATE, FOREIGN KEY (user_id) REFERENCES customer(user_id));")
cursor.execute("""CREATE TABLE IF NOT EXISTS order_items (
               order_item_id INT AUTO_INCREMENT PRIMARY KEY, 
               order_id INT, 
               product_id INT, 
               quantity INT, 
               FOREIGN KEY (order_id) REFERENCES orders(order_id), 
               FOREIGN KEY (product_id) REFERENCES products(product_id)
               );""")
mydb.commit()

def clear():
    print("\n" * 50)

def create_account():
    email = input("Enter your email to create a new account: ")
    name = input("Enter your name: ")

    try:
        cursor.execute("INSERT INTO customer (name, email) VALUES (%s, %s)", (name, email))
        mydb.commit()
        print("Account created!\n\n")
        input()
        sign_in()

    except mysql.connector.Error as err:
        print("Account already exists. Please sign in with an existing account or sign up with an unused email.")
        input()

def add_item(cart):
    cursor.execute("SELECT * FROM products;")
    results = cursor.fetchall()

    for product_id, item_name, rating, cost in results:
        print(f"ID: {product_id:<4} | Item: {item_name:<20} | Rating: {rating}/5 | Price: ${cost:>8}")
    print("")

    try:
        item_id = int(input("Enter the product id for the item you would like to add to your cart: "))
        quant = int(input("Enter the quantity of the item you selected: "))
    except ValueError:
        print("Please enter a valid numerical value.")
        return

    cursor.execute("SELECT * FROM products WHERE product_id = %s", (item_id,))
    results = cursor.fetchone()

    if (results):
        found = False
        for item in cart:
            if item["ID"] == item_id:
                item["Quantity"] += quant
                found = True
                break

        if not found:
            cart.append({
                "ID": results[0],
                "Name": results[1],
                "Cost": results[3],
                "Quantity": quant
            })
        print("Item added to cart!")
        input()
    
    else:
        print("Item does not exist, please enter a valid item id.")
        input()

def remove_item(cart):
    found = False
    if not cart:
        print("Cart is empty.")
        input()
        return
    for item in cart:
        print(f"ID: {item['ID']}, {item['Name']} x{item['Quantity']} for ${item['Cost']} each")
    print("")

    item_id = int(input("Enter the product id for the item you would like to remove from your cart: "))
    for item in cart:
        if item["ID"] == item_id:
            cart.remove(item)
            found = True
            print("Item removed from cart!")
            input()
            break

    if not found:
        print("Item not found in cart.")
        input()

def display(cart):
    if not cart:
        print("Cart is empty.")
        input()
        return
    
    for item in cart:
        print(f"ID: {item['ID']}, {item['Name']} x{item['Quantity']} for ${item['Cost']} each")
    input()

def checkout(cart, email):
    if not cart:
        print("Cart is empty.")
        input()
        return
    
    cursor.execute("SELECT user_id FROM customer WHERE email = %s", (email,))
    user = cursor.fetchone()
    user_id = user[0]

    cursor.execute("INSERT INTO orders (user_id, order_date) VALUES (%s, NOW())", (user_id,))
    order_id = cursor.lastrowid

    cost = Decimal('0.0')
    for item in cart:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)", (order_id, item['ID'], item['Quantity']))
        cost += item['Cost']*item['Quantity']
    mydb.commit()
    cart.clear()
    print(f"Order placed successfully!")
    print(f"Subtotal: ${cost:.2f}")
    print(f"Total with tax: ${cost*Decimal("1.13"):.2f}")
    input()
    return

def sign_in():
    email = input("Enter your email to sign in: ")

    cursor.execute("SELECT * FROM customer WHERE email = %s", (email,)) 
    result = cursor.fetchone()

    if (result):
        cart = []
        print(f"\nWelcome back, {result[1]}!")
        input()
        while True:
            clear()
            print("\nWhat action would you like to do?")
            print("1: Add item to cart.")
            print("2: Remove item from cart.")
            print("3: Display cart.")
            print("4: Checkout.")
            print("5: Log out.\n")

            choice = input("Please enter your choice: ")

            if(choice == "1"):
                add_item(cart)
            elif(choice == "2"):
                remove_item(cart)
            elif(choice == "3"):
                display(cart)
            elif(choice == "4"):
                checkout(cart, email)
            elif(choice == "5"):
                print(f"\nGoodbye {result[1]}!")
                input()
                break
            else:
                print("Please enter a valid option.")
                input()
    else:
        print("No account found. Please sign in using an existing registered email or sign up.")
        input()

def order_history():
    sql = """SELECT 
    orders.order_id,
    customer.name,
    SUM(products.cost * order_items.quantity) * 1.13 AS total,
    orders.order_date
    FROM order_items
    JOIN orders
        ON order_items.order_id = orders.order_id
    JOIN customer
        ON orders.user_id = customer.user_id
    JOIN products
        ON order_items.product_id = products.product_id
    GROUP BY 
        orders.order_id,
        customer.name,
        orders.order_date
    ORDER BY orders.order_id;
    """

    cursor.execute(sql)
    results = cursor.fetchall()

    print("\nPlease note, the dollar amounts shown include tax.\n")

    for order_id, name, total, order_date in results:
        print("-------------------------------------------------------------------------------------------------------------------------------------")
        print(f"Order ID: {order_id:<3} | Customer: {name:<15} | Total: ${total:<3.2f} | Order date: {str(order_date):>6}")
    print("-------------------------------------------------------------------------------------------------------------------------------------")
    input()
    return

def detailed_history():
    sql = """SELECT
    order_items.order_item_id,
    order_items.order_id,
    customer.name,
    products.item_name,
    order_items.quantity,
    products.cost * order_items.quantity AS subtotal,
    orders.order_date
    FROM order_items
    JOIN orders
        ON order_items.order_id = orders.order_id
    JOIN customer
        ON orders.user_id = customer.user_id
    JOIN products
        ON order_items.product_id = products.product_id
    ORDER BY order_items.order_item_id;
    """
    cursor.execute(sql)
    results = cursor.fetchall()

    print("\nPlease note, the dollar amounts shown do not include tax.\n")

    for id, order_id, name, item, quantity, subtotal, order_date in results:
        print("------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"#{id}: Order ID: {order_id:<4} | Customer: {name:<25} | Product: {item:<25} | Quantity: {quantity:<4} | Cost: {subtotal:<10.2f} | Purchase date: {str(order_date):>10}")
    print("------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    input()
    return

while True:
    clear()
    print("\n==================== The Transaction Management System Version 1 ====================\n")
    print("Hello! Welcome to the TMS V1. What action would you like to take?\n")
    print("1: Sign up.")
    print("2: Sign in.")
    print("3. View all orders.")
    print("4. View all orders in detail.\n")
    choice = input("Please enter your choice: ")

    if(choice == "1"):
        create_account()
    elif(choice == "2"):
        sign_in()
    elif(choice == "3"):
        order_history()
    elif(choice == "4"):
        detailed_history()
    else:
        print("Please enter a valid choice.")
        input()

    print("\n======================================================================================\n")
    

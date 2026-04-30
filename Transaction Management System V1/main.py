import os
import mysql.connector
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
        print("Account created!\n")

    except mysql.connector.Error as err:
        print("Account already exists. Please sign in with an existing account or sign up with an unused email.")

def add_item(cart):
    cursor.execute("SELECT * FROM products;")
    results = cursor.fetchall()

    for x in results:
        print(x)
    print("")

    item_id = int(input("Enter the product id for the item you would like to add to your cart: "))
    quant = int(input("Enter the quantity of the item you selected: "))

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

def remove_item(cart):
    found = False
    if not cart:
        print("Cart is empty.")
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

def display(cart):
    if not cart:
        print("Cart is empty.")
        return
    
    for item in cart:
        print(f"ID: {item['ID']}, {item['Name']} x{item['Quantity']} for ${item['Cost']} each")
        input()

def checkout(cart, email):
    if not cart:
        print("Cart is empty.")
        return
    
    cursor.execute("SELECT user_id FROM customer WHERE email = %s", (email,))
    user = cursor.fetchone()
    user_id = user[0]

    cursor.execute("INSERT INTO orders (user_id, order_date) VALUES (%s, NOW())", (user_id,))
    order_id = cursor.lastrowid

    for item in cart:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)", (order_id, item["ID"], item["Quantity"]))
    mydb.commit()
    cart.clear()
    print("Order placed successfully!")
    input()
    return

def sign_in():
    email = input("Enter your email to sign in: ")

    cursor.execute("SELECT * FROM customer WHERE email = %s", (email,)) 
    result = cursor.fetchone()

    if (result):
        cart = []
        while True:
            clear()
            print(f"\Welcome back, {result[1]}!")
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
    else:
        print("No account found. Please sign in using an existing registered email or sign up.")

while True:
    clear()
    print("\n==================== The Transaction Management System Version 1 ====================\n")
    print("Hello! Welcome to the TMS V1. What action would you like to take?\n")
    print("1: Sign up.")
    print("2: Sign in.\n")
    choice = input("Please enter your choice: ")

    if(choice == "1"):
        create_account()
    elif(choice == "2"):
        sign_in()
    else:
        print("Please enter a valid choice.")

    print("\n======================================================================================\n")
    

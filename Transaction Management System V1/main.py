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
cursor.execute("CREATE TABLE IF NOT EXISTS customer (user_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255) UNIQUE;")
cursor.execute("CREATE TABLE IF NOT EXISTS orders (order_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, order_date DATE, FOREIGN KEY (user_id) REFERENCES users(user_id));")
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

def sign_in():
    email = input("Enter your email to sign in: ")

    cursor.execute("SELECT * FROM customer WHERE email = %s", (email,)) 
    result = cursor.fetchone()

    if (result):
        while True:
            clear()
            print(f"\Welcome back, {result[1]}!")
            print("\nWhat action would you like to do?")
            print("1: Add item to cart.")
            print("2: Remove item from cart.")
            print("3: Checkout.")
            print("4: Log out.\n")

            choice = input("Please enter your choice: ")

            if(choice == "1"):
                add_item()
            elif(choice == "2"):
                remove_item()
            elif(choice == "3"):
                checkout()
            elif(choice == "4"):
                print(f"\nGoodbye {result[1]}!")
                input()
                break
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
    

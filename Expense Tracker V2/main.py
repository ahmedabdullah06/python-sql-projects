import os
import mysql.connector
import bcrypt
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255) UNIQUE, password VARCHAR(255));")
mycursor.execute("CREATE TABLE IF NOT EXISTS expenditures (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, date_purchased DATE, item_name VARCHAR(255), description VARCHAR(255), cost DECIMAL(10,2), FOREIGN KEY (user_id) REFERENCES users(user_id));")

#This is the pin for the admin
global pin
with open("pin.txt", "r") as file:
    pin = int(file.read())

def clear():
  print("\n" * 40)

def create_account():
    email = input("Enter your email to create a new account: ")
    password = input("Enter your password: ")
    name = input("Enter your name: ")
    hashed_password = bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()

    try:
        mycursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mydb.commit()
        print("Account created!\n")
        input()
        sign_in()

    except mysql.connector.Error as err:
        print("Account already exists. Please sign in with an existing account or sign up with an unused email.")
        input()

def remove_expense(user_id):
  display_expenses(user_id)

  expense_id = num_check("Enter the ID of the entry you want to remove from your expense log: ")
  if expense_id == -1:
     return
  
  mycursor.execute("DELETE FROM expenditures WHERE user_id = %s AND id = %s", (user_id, expense_id))
  mydb.commit()

  if mycursor.rowcount == 0:
    print("No matching entry found.")
    input()
  else:
    print("Entry deleted!")
    input()

def add_expense(user_id):
    item = input("Enter item name: ")
    date = input("Enter date of purchase in the format 'yyyy-mm-dd': ")
    choice2 = input("Would you like to add an item description? y/n: ")
    description = "No description"
    try:
        cost = Decimal(input("Enter item cost: "))
    except:
        print("Invalid cost.")
        input()
        return

    if choice2.lower() in ('y', 'yes'):
      description = input("Enter a short description: ")
    
    sql = "INSERT INTO expenditures (user_id, date_purchased, item_name, description, cost) VALUES (%s, %s, %s, %s, %s);"
    mycursor.execute(sql, (user_id, date, item, description, cost))
    mydb.commit()
    print("Entry added!")
    input()

def display_expenses(user_id):
    print("\nYour current expenses:\n")
    mycursor.execute("SELECT * FROM expenditures WHERE user_id = %s", (user_id,))
    result = mycursor.fetchall()

    if(result):
        for id, _, date, item, description, cost in result:
            print(f"ID: {id:<4} | Purchase date: {str(date):<14} | Item: {item:<20} | Cost: ${cost:<8} | Description: {description:>20}")
        input()
    else:
        print("No expenses entered.")
        input()
    print()

def alter_description(user_id):
    display_expenses(user_id)
    entry_id = num_check("Select entry ID: ")
    if not entry_id:
       return
    desc = input("Enter a description for the item: ")
    sql = "UPDATE expenditures SET description = %s WHERE id = %s AND user_id = %s;"
    mycursor.execute(sql, (desc, entry_id, user_id))
    mydb.commit()

    if mycursor.rowcount == 0:
        print("No expense with that ID.")
        input()
    else:
        print("Description updated.")
        input()

def monthly_expenses(user_id):
  sql = """
  SELECT
  YEAR(date_purchased),
  MONTH(date_purchased),
  SUM(cost)
  FROM expenditures
  WHERE user_id = %s
  GROUP BY YEAR(date_purchased), MONTH(date_purchased)
  ORDER BY YEAR(date_purchased) DESC, MONTH(date_purchased) DESC;
  """
  mycursor.execute(sql, (user_id,))
  result = mycursor.fetchall()

  if(result):
    for year, month, cost in result:
      print(f"Year: {year}, month of {month}: total cost: ${cost:>8.2f}")
  else:
      print("No logged expenses.")  

def display_all():
    mycursor.execute("""
    SELECT
        expenditures.id,
        users.name,
        users.email,
        expenditures.item_name,
        expenditures.cost,
        expenditures.date_purchased
    FROM expenditures
    JOIN users 
        ON expenditures.user_id = users.user_id
    ORDER BY users.name ASC, date_purchased DESC
    """)
    output = mycursor.fetchall()

    print("\n==================== All User Expenses ====================\n")

    for id, name, email, item, cost, date in output:
        print(
            f"ID: {id:<4} | "
            f"Name: {name:<15} | "
            f"Email: {email:<20} | "
            f"Item: {item:<25} | "
            f"Cost: ${cost:>8.2f} | "
            f"Date: {str(date):<12}"
        )

    print("\n===========================================================\n")
   
def sign_in():
    email = input("Enter your email to sign in: ")
    password = input("Enter your password: ")
    
    mycursor.execute("SELECT * FROM users WHERE email = %s", (email,)) 
    result = mycursor.fetchone()

    if(result and bcrypt.checkpw(password.encode(), result[3].encode())):
        user_id = result[0]

        print(f"\nWelcome back, {result[1]}!")
        input()
        while True:
            clear()
            print("\n1. Add expense.")
            print("2. Remove expense.")
            print("3. View total expenses.")
            print("4. View monthly expenses.")
            print("5. Add/replace description.")
            print("6. Log out\n")

            choice = input("Please enter your choice: ")

            if(choice == "1"):
                add_expense(user_id)
            elif(choice == "2"):
                remove_expense(user_id)
            elif(choice == "3"):
                display_expenses(user_id)
            elif(choice == "4"):
                monthly_expenses(user_id)
            elif(choice == "5"):
                alter_description(user_id)
            elif(choice == "6"):
                print(f"\nGoodbye {result[1]}!")
                input()
                break
            else:
                print("Please enter a valid option.")
                input()
    else:
        print("The email or the password entered are invalid. Please try again.")
        input()

def change_password():
    email = input("Enter your email: ")
    mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = mycursor.fetchone()
    if result:
       password = input("Enter your password: ")
       if(bcrypt.checkpw(password.encode(), result[3].encode())):
          print("Confirmed, now you can change your password!")
          new_password = input("Enter your new password: ")
          new_hashed_password = bcrypt.hashpw(new_password.encode(),bcrypt.gensalt()).decode()
          mycursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_hashed_password, email))
          mydb.commit()
          print("Password changed!")
          input()
    else:
       print("This email does not exist, please create an account or use a registered email.")   

def num_check(prompt) -> int:
    try:
        val = int(input(prompt))
    except ValueError:
        print("Please input an appropriate numerical value.")
        input()
        return 0
    return val

def admin():
   print("You are in the admin login page, please confirm your identity by entering the admin pin or '0' to exit.")
   input_pin = num_check("PIN: ")

   if input_pin and input_pin == pin: #Arbitray pin set by the admin
        print("Welcome back, Admin!")
        input()

        while True:
            print("1. View all expenses.")
            print("2. Export all expenses as a CSV.")
            print("3. Change pin.")
            print("4. Log out.")

            choice = input("Enter your choice of action, Admin: ")

            if choice == "1":
               display_all()
            elif choice == "2":
               export_csv()
            elif choice == "3":
               new_pin = num_check("Enter a new pin Admin: ")
               if new_pin:
                  pin = new_pin
                  with open("pin.txt", "w") as file:
                    file.write(str(new_pin))
            elif choice == "4":
               print("Have a nice day Admin, goodbye!")
               input()
               break
            else:
               print("Invalid input, please try again.")
               input()

while True:
    print("\n------------------------- Expense Tracker V2 -------------------------\n")
    print("Welcome to the Expense Tracker Version 2!\n")
    print("1. Sign up.")
    print("2. Sign in.")
    print("3. Change password.")
    print("4. Admin login.")

    choice = input("Please enter your choice of action: ")

    if choice == "1":
       create_account()
    elif choice == "2":
       sign_in()
    elif choice == "3":
       change_password()
    elif choice == "4":
       admin()
    else:
       print("Invalid input, please enter a valid choice.")
    print("\n----------------------------------------------------------------------\n")


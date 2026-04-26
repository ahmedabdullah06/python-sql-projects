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

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS expenditures (id INT AUTO_INCREMENT PRIMARY KEY, date_purchased DATE, item_name VARCHAR(255), description VARCHAR(255), cost DECIMAL(10, 2));")


#Functions
def add_expense(date, name, desc, amount):
  sql = "INSERT INTO expenditures (date_purchased, item_name, description, cost) VALUES (%s, %s, %s, %s);"
  mycursor.execute(sql, (date, name, desc, amount))
  mydb.commit()

def total_expenses():
  mycursor.execute("SELECT SUM(cost) FROM expenditures;")
  result = mycursor.fetchone()
  print("\nTotal: %.2f", result[0])

def remove_expense_id(id):
  check_sql = "SELECT * FROM expenditures WHERE id=%s;"
  mycursor.execute(check_sql, (id,))
  result = mycursor.fetchone()

  if result is None:
      print("\nItem with id %s not found.", id)
      return

  delete_sql = "DELETE FROM expenditures WHERE id = %s;"
  mycursor.execute(delete_sql, (id,))
  mydb.commit()

  print("\nExpense deleted.")

def remove_expense_name(item_name):
  check_sql = "SELECT * FROM expenditures WHERE item_name = %s;"
  mycursor.execute(check_sql, (item_name,))
  result = mycursor.fetchone()

  if result is None:
      print("\nItem with item name \"%s\" not found.", item_name)
      return

  delete_sql = "DELETE FROM expenditures WHERE item_name = %s;"
  mycursor.execute(delete_sql, (item_name,))
  mydb.commit()

  print("\nExpense deleted.")

def expenses_month():
  sql = """
  SELECT
  YEAR(date_purchased),
  MONTH(date_purchased),
  SUM(cost)
  FROM expenditures
  GROUP BY YEAR(date_purchased), MONTH(date_purchased)
  ORDER BY YEAR(date_purchased) DESC, MONTH(date_purchased) DESC;
  """
  mycursor.execute(sql)
  result = mycursor.fetchall()
  for i in result:
    print(i)

def print_table():
  sql = "SELECT * FROM expenditures"
  mycursor.execute(sql)
  results = mycursor.fetchall()

  print("\n")
  for i in results:
    print(i)

while True:
  choice = ""
  choice2 = ""
  print("\n====== Expense Tracker ======")
  print("1. Add expense")
  print("2. Remove expense")
  print("3. View total expenses")
  print("4. View monthly expenses")
  print("5. Add/replace description")
  print("6. Print table")

  choice = input("What would you like to do? ")

  match choice:
    case "1":
      item = input("Enter item name: ")
      date = input("Enter date of purchase in the format 'yyyy-mm-dd': ")
      cost = float(input("Enter item cost: "))
      choice2 = input("Would you like to add an item description? y/n: ")
      description = "No description"

      if choice2.lower() in ('y', 'yes'):
        description = input("Enter a short description: ")

      add_expense(date, item, description, cost)

    case "2":
      print("1. Remove by ID")
      print("2. Remove by item name")

      choice2 = input("Choose your method of deletion: ")
      
      if(choice2 == "1"):
        id = input("Enter the ID for the item you would like to delete: ")
        remove_expense_id(id)

      if(choice2 == "2"):
        item_name = input("Enter the name for the item you would like to delete: ")
        remove_expense_name(item_name)

    case "3":
      total_expenses()
    
    case "4":
      expenses_month()
    
    case "6":
      print_table()

    case _:
      print("Invalid input, please try again.")
  print("\n=============================\n")







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
mycursor.execute("CREATE TABLE expenditures (id INT AUTO_INCREMENT PRIMARY KEY, date_purchased DATE, item_name VARCHAR(255), description VARCHAR(255), cost FLOAT)")


#Functions
def add_expense(date, name, desc, amount):
  sql = "INSERT INTO expenditures (date_purchased, item_name, description, cost) VALUES (%s, %s, %s, %s)"
  mycursor.execute(sql, (date, name, desc, amount))
  mydb.commit()

def total_expense():
  mycursor.execute("SELECT SUM(cost) FROM expenditures")


while True:
  choice = ""
  choice2 = ""
  print("\n====== Expense Tracker ======")
  print("1. Add expense")
  print("2. Remove expense")
  print("3. View total expenses")
  print("4. View expenses by year")
  print("5. Add/replace description")
  print("6. Print table")

  choice = input("What would you like to do? ")

  match choice:
    case "1":
      item = input("Enter item name: ")
      date = input("Enter date of purchase in the format 'yyyy-mm-dd': ")
      cost = float(input("Enter item cost: "))
      choice2 = input("Would you like to add an item description? y/n: ")
      description = "None"

      if(choice2.capitalize() == "Y" or choice2.capitalize() == "YES"):
        description = input("Enter a short description: ")

      add_expense(date, item, description, cost)






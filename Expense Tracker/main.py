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

while True:
  print("\n=== Expense Tracker ===")
  print("1. Add expense")
  print("2. Remove expense")
  print("3. View total")
  print("4. Add/replace description")
  print("5. Print table")

  choice = input("What do you want to do? ")

def add_expense(date, name, desc, amount):
  sql = "INSERT INTO expenditures (date_purchased, item_name, description, cost) VALUES (%s, %s, %s, %s)"
  mycursor.execute(sql, (date, name, desc, amount))
  mydb.commit()





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

#expenditures (datePurchased DATE, itemName VARCHAR(255), cost FLOAT)

sql = "UPDATE expenditures SET item_name = 'Mercedes 300E' WHERE item_name = 'Car'" #"SELECT item_name  FROM expenditures WHERE YEAR(date_purchased) >= 2024 ORDER BY item_name DESC"
"""val = [
  ('2025-01-27', "Car", 44000),
  ('2025-08-21', "Tax return", -400),
  ('2026-01-02', "Wage", -4000),
  ('2025-11-07', "TV", 2000),
  ('2024-09-27', "Al-Baik", 70.65),
  ('2023-01-27', "Washing machine", 4030.23),
  ('2018-04-19', "Rent", 1500),
  ('2026-04-02', "Bike", 200.54),
  ('2025-10-03', "Chair", 141.34),
  ('2024-11-07', "Bills", 700.98),
]"""

#mycursor.executemany(sql, val)
mycursor.execute(sql)
mydb.commit()
print(mycursor.rowcount, "record(s) affected")




import pandas as pd
import mysql.connector

file_path = 'C:\\Users\\kaany\\Downloads\\volleydb.xlsx'
xls = pd.ExcelFile(file_path)

data = {}

for sheet_name in xls.sheet_names:
    data[sheet_name] = pd.read_excel(xls, sheet_name)
    

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1a2w3s4r.kaan",
    database="volleydb"
)
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255),
    name VARCHAR(255),
    surname VARCHAR(255)
);
''')
conn.commit()
    



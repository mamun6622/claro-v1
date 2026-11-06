import sqlite3

connection = sqlite3.connect("claro.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT id, title, url, LENGTH(content)
    FROM knowledge
""")

records = cursor.fetchall()

for record in records:
    print("\nID:", record[0])
    print("Title:", record[1])
    print("URL:", record[2])
    print("Content length:", record[3])

connection.close()
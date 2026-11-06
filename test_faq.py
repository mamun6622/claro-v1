
import sqlite3

DATABASE_FILE = "claro.db"

connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute("""
    SELECT id, category, question, answer, keywords
    FROM faq
    ORDER BY id
""")

rows = cursor.fetchall()

print("\n========== CLARO FAQ DATABASE ==========\n")

for row in rows:
    faq_id, category, question, answer, keywords = row

    print(f"ID: {faq_id}")
    print(f"Category: {category}")
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    print(f"Keywords: {keywords}")
    print("-" * 60)

print(f"\nTOTAL FAQ RECORDS: {len(rows)}")

connection.close()

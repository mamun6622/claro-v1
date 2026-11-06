import sqlite3
import json

DATABASE_NAME = "claro.db"
JSON_FILE = "bic_knowledge.json"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("Database is ready.")


def import_knowledge():
    # Read the existing JSON file
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        knowledge_data = json.load(file)

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Remove old records to prevent duplicates
        cursor.execute("DELETE FROM knowledge")

        # Insert the JSON records into SQLite
        for item in knowledge_data:
            cursor.execute("""
                INSERT INTO knowledge (url, title, content)
                VALUES (?, ?, ?)
            """, (
                item["url"],
                item["title"],
                item["text"]
            ))

        connection.commit()

        print(f"Successfully imported {len(knowledge_data)} records.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    import_knowledge()
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=== Quiz ===")
cursor.execute("SELECT * FROM Quiz")
print(cursor.fetchall())

print("\n=== Questions ===")
cursor.execute("SELECT * FROM Questions")
print(cursor.fetchall())

print("\n=== Choices ===")
cursor.execute("SELECT * FROM Choices")
print(cursor.fetchall())

print("\n=== Lessons ===")
cursor.execute("SELECT * FROM Lessons")
print(cursor.fetchall())

conn.close()
 
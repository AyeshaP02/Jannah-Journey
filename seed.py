import sqlite3

conn = sqlite3.connect('database.db') 
cursor = conn.cursor()

with open ('lesson_quiz_schema.sql', 'r') as f:
    schema = f.read()
    cursor.executescript(schema)

# ── Users ─────────────────────────────────────────────────
#cursor.executemany("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", [
#   ("admin_teacher", "password123", "teacher"),
  #  ("student_ali", "password123", "student"),
   # ("student_fatima", "password123", "student"),
#])

# ── Lessons ───────────────────────────────────────────────
cursor.executemany("INSERT INTO Lessons (title, topic, content) VALUES (?, ?, ?)", [
    (
        "The Life of Prophet Ibrahim (AS)",
        "Prophets & Stories",
        "Prophet Ibrahim (AS) is known as the father of the prophets. He was born in Babylon and grew up to reject idol worship. He built the Kaaba with his son Prophet Ismail (AS) in Makkah."
    ),
    (
        "The 5 Pillars of Islam",
        "Prayer & Pillars",
        "The five pillars of Islam are: Shahada (declaration of faith), Salah (prayer five times daily), Zakat (charity), Sawm (fasting in Ramadan), and Hajj (pilgrimage to Makkah)."
    ),
    (
        "Surah Al-Fatiha & Daily Duas",
        "Duas & Surahs",
        "Surah Al-Fatiha is the opening chapter of the Quran with 7 verses. It is recited in every unit of prayer. Common daily duas include Bismillah before eating and Alhamdulillah after eating."
    ),
])

# ── Quizzes ───────────────────────────────────────────────
cursor.executemany("INSERT INTO Quiz (lesson_ID, title) VALUES (?, ?)", [
    (1, "Quiz: The Prophets"),
    (2, "Quiz: The 5 Pillars"),
    (3, "Quiz: Duas & Surahs"),
])

# ── Questions ─────────────────────────────────────────────
cursor.executemany("INSERT INTO Questions (quiz_ID, question_text) VALUES (?, ?)", [
    # Quiz 1 - Prophets (quiz_ID = 1)
    (1, "Which prophet built the Kaaba?"),
    (1, "Which prophet parted the sea?"),

    # Quiz 2 - 5 Pillars (quiz_ID = 2)
    (2, "How many times do Muslims pray per day?"),
    (2, "What is the first pillar of Islam?"),

    # Quiz 3 - Duas & Surahs (quiz_ID = 3)
    (3, "How many verses does Surah Al-Fatiha have?"),
    (3, "Which surah is known as the heart of the Quran?"),
])

# ── Choices ───────────────────────────────────────────────
cursor.executemany("INSERT INTO Choices (question_ID, choice_text, is_correct) VALUES (?, ?, ?)", [
    # Q1 - Who built the Kaaba?
    (1, "Prophet Ibrahim (AS)", 1),
    (1, "Prophet Musa (AS)", 0),
    (1, "Prophet Isa (AS)", 0),
    (1, "Prophet Nuh (AS)", 0),

    # Q2 - Who parted the sea?
    (2, "Prophet Musa (AS)", 1),
    (2, "Prophet Dawud (AS)", 0),
    (2, "Prophet Yusuf (AS)", 0),
    (2, "Prophet Ibrahim (AS)", 0),

    # Q3 - How many prayers?
    (3, "5", 1),
    (3, "3", 0),
    (3, "7", 0),
    (3, "4", 0),

    # Q4 - First pillar?
    (4, "Shahada", 1),
    (4, "Salah", 0),
    (4, "Zakat", 0),
    (4, "Sawm", 0),

    # Q5 - Verses in Al-Fatiha?
    (5, "7", 1),
    (5, "5", 0),
    (5, "10", 0),
    (5, "6", 0),

    # Q6 - Heart of the Quran?
    (6, "Surah Ya-Sin", 1),
    (6, "Surah Al-Baqarah", 0),
    (6, "Surah Al-Ikhlas", 0),
    (6, "Surah Al-Kahf", 0),
])

conn.commit()
conn.close()
print("✅ Seed data inserted successfully!")

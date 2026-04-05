from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'database.db'

#helper function to connect to DB
def get_db():
    return sqlite3.connect(DB_NAME)


# Save Lesson

@app.route('/create_lesson', methods=['GET', 'POST'])
def create_lesson():
    if request.method == 'POST':
        title = request.form['title']
        topic = request.form['topic']
        content = request.form['content']

        #basic validation
        if not title or not content:
            return "Error: Title and Content are required"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO Lessons(title, topic, content,) VALUES (?, ?, ?)""", (title, topic, content))
        conn.commit()
        conn.close()
    
        return redirect('/lessons') 
    return render_template('create_lesson.html')



# Display Lessons
@app.route('/lessons')
def lessons():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Lessons")
    lessons = cursor.fetchall()

    conn.close()

    return render_template('lessons.html', lessons = lessons)


# F3.2 + # F3.3 -- Create Quiz + Store in Database
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form['title']

        conn = get_db()
        cursor = conn.cursor()

        # Insert quiz
        cursor.execute("INSERT INTO Quiz (title) VALUES (?)", (title,))
        quiz_ID = cursor.lastrowid

        # Loop through questions
        i = 1
        while f'question_{i}' in request.form:
            question_text = request.form[f'question_{i}']

            cursor.execute(
                "INSERT INTO Questions (quiz_ID, question_text) VALUES (?, ?)",
                (quiz_ID, question_text)
            )
            question_ID = cursor.lastrowid

            # Insert answers
            for j in range(1, 5):
                choice_text = request.form[f'answer_{i}_{j}']
                is_correct = int(request.form[f'correct_{i}']) == j

                cursor.execute(
                    "INSERT INTO Choices (question_ID, answer_text, is_correct) VALUES (?, ?, ?)",
                    (question_ID, choice_text, is_correct)
                )

            i += 1

        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('create_quiz.html')



# F4.1 Display Quiz
@app.route('/quiz/<int:quiz_ID>')
def take_quiz(quiz_ID):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Quiz WHERE quiz_ID=?", (quiz_ID,))
    quiz = cursor.fetchone()

    cursor.execute("SELECT * FROM Questions WHERE quiz_ID=?", (quiz_ID,))
    questions = cursor.fetchall()

    quiz_data = []

    for q in questions:
        cursor.execute("SELECT * FROM Choices WHERE question_ID=?", (q[0],))
        answers = cursor.fetchall()
        quiz_data.append((q, answers))

    conn.close()

    return render_template('take_quiz.html', quiz=quiz, quiz_data=quiz_data)

#F4.2 Quiz Scoring 

@app.route('/submit_quiz/<int:quiz_ID>', methods=['POST'])
def submit_quiz(quiz_ID):
    conn = get_db()
    cursor = conn.cursor()

    score = 0
    total = 0

    cursor.execute("SELECT question_ID FROM Questions WHERE quiz_ID=?", (quiz_ID,))
    questions = cursor.fetchall()

    for q in questions:
        q_id = q[0]
        selected = request.form.get(f'question_{q_id}')

        cursor.execute(
            "SELECT is_correct FROM Choices WHERE choice_ID=?",
            (selected,)
        )
        result = cursor.fetchone()

        if result and result[0] == 1:
            score += 1

        total += 1

    conn.close()

    return f"Your Score: {score} / {total}"


@app.route('/')
def home():
    return "<h1>Quiz System Running</h1>"


if __name__ == '__main__':
    app.run(debug=True)


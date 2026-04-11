from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
DB_NAME = 'database.db'


#helper function to connect to DB
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")  #this enforces FK constraints
    return conn




#F1.2 -- Display Lessons
# Display Lessons
@app.route('/lessons')
def lessons():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lessons")
    lessons = cursor.fetchall()

    conn.close()

    return render_template('lessons.html', lessons = lessons)

#View Lesson 
@app.route('/lesson/<int:lesson_ID>')
def view_lesson(lesson_ID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lessons WHERE lesson_ID=?", (lesson_ID,))
    lesson = cursor.fetchone()
    conn.close()

    if not lesson:
        return "Lesson not found", 404
    return render_template('view_lesson.html', lesson=lesson)


#F2.2 & F2.2 -- Create Lesson + save to Database
@app.route('/create_lesson', methods=['GET', 'POST'])
def create_lesson():
    if request.method == 'POST':
        title = request.form['title']
        topic = request.form['topic']
        content = request.form['content']

        #basic validation
        if not title or not content:
            return render_template('create_lesson.html', error ="Error: Title and Content are required")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Lessons(title, topic, content) VALUES (?, ?, ?)", (title, topic, content,))
        conn.commit()
        conn.close()
   
        return redirect(url_for('lessons'))
    return render_template('create_lesson.html')





#F1.3 Edit or Delete a lesson

@app.route('/edit_lesson/<int:lesson_ID>', methods=['GET', 'POST'])
def edit_lesson(lesson_ID):
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        topic = request.form.get('topic')

        if not title or not content:
            return render_template('edit_lesson.html', error="Title and Content are required")
        cursor.execute(
            "UPDATE Lessons SET title=?, topic=?, content=? WHERE lesson_ID=?",
            (title, topic, content, lesson_ID)
            )
        conn.commit()
        return redirect(url_for('lessons'))

    cursor.execute("SELECT * FROM Lessons WHERE lesson_ID=?", (lesson_ID,))
    lesson = cursor.fetchone()
    
    conn.close()

    if not lesson:
        return "Lesson not found", 404
    return render_template('edit_lesson.html', lesson=lesson)


@app.route('/delete_lesson/<int:lesson_ID>', methods=['POST'])
def delete_lesson(lesson_ID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Lessons WHERE lesson_ID=?", (lesson_ID,))
    conn.commit()
    conn.close()

    return redirect(url_for('lessons'))





# F3.2 + # F3.3 -- Create Quiz + Store in Database
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()

        if not title:
            return render_template('create_quiz.html', error="Quiz title is required")

        # Check at least one question was submitted
        if 'question_1' not in request.form:
            return render_template('create_quiz.html', error="At least one question is required")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Quiz (title) VALUES (?)", (title,))
        quiz_ID = cursor.lastrowid

        i = 1
        while f'question_{i}' in request.form:
                question_text = request.form[f'question_{i}'].strip()

                # Fixed: no longer inserting correct_answer since we use is_correct on Choices
                cursor.execute(
                    "INSERT INTO Questions (quiz_ID, question_text) VALUES (?, ?)",
                    (quiz_ID, question_text)
                )
                question_ID = cursor.lastrowid

                for j in range(1, 5):
                    choice_text = request.form.get(f'answer_{i}_{j}', '').strip()
                    is_correct = int(request.form.get(f'correct_{i}', 0)) == j

                    cursor.execute(
                        "INSERT INTO Choices (question_ID, choice_text, is_correct) VALUES (?, ?, ?)",
                        (question_ID, choice_text, int(is_correct))
                    )

                i += 1

        conn.commit()
        conn.close()

        return redirect(url_for('home'))
    return render_template('create_quiz.html')



# F4.1 Display Quiz
@app.route('/take_quiz/<int:quiz_ID>')
def take_quiz(quiz_ID):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Quiz WHERE quiz_ID=?", (quiz_ID,))
    quiz = cursor.fetchone()

    if not quiz:
        return "quiz not found"
    
    cursor.execute("SELECT * FROM Questions WHERE quiz_ID=?", (quiz_ID,))
    questions = cursor.fetchall()

    quiz_data = []
    for q in questions:
        cursor.execute("SELECT * FROM Choices WHERE question_ID=?", (q[0],))
        choices = cursor.fetchall()
        quiz_data.append((q, choices))

    conn.close()

    return render_template('take_quiz.html', quiz=quiz, quiz_data=quiz_data)


#F4.2 & F4.3 Quiz Scoring + Save Result
@app.route('/submit_quiz/<int:quiz_ID>', methods=['POST'])
def submit_quiz(quiz_ID):
    conn = get_db()
    cursor = conn.cursor()

    score = 0
    total = 0

    user_id = session.get('user_ID')
    cursor.execute("SELECT question_ID FROM Questions WHERE quiz_ID=?", (quiz_ID,))
    questions = cursor.fetchall()

    for q in questions:
        q_id = q[0]
        selected = request.form.get(f'question_{q_id}')
        total += 1

        if selected is None:
            continue

        cursor.execute(
            "SELECT is_correct FROM Choices WHERE choice_ID=?",
            (selected,)
        )
        result = cursor.fetchone()

        if result and result[0] == 1:
            score += 1

# F4.3 Store result in database
    cursor.execute(
        "INSERT INTO Quiz_Results (quiz_ID, score) VALUES (?, ?)",
        (quiz_ID, score)
    )
    conn.commit()
    conn.close()

    return f"<h2>Score: {score} / {total}</h2><a href='/progress'>View Progress</a>"



#F5.1 Progress
@app.route('/progress')
def progress():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Quiz.title, Quiz_Results.score, Quiz_Results.completion_date
        FROM Quiz_Results
        JOIN Quiz ON Quiz_Results.quiz_ID = Quiz.quiz_ID
        WHERE Quiz_Results.user_ID = ?
        ORDER BY Quiz_Results.completion_date DESC """, (session.get('user_ID'),))
    
    data = cursor.fetchall()
    conn.close()
    return render_template('student_progress.html', results=data)


@app.route('/')
def home():
    return redirect('/lessons')


if __name__ == '__main__':
    app.run(debug=True)

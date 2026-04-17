from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'jannah_8' # ensure data integrity, helps validate cookies.
DB_NAME = 'database.db'


#helper function to connect to DB
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")  #this enforces FK constraints
    return conn



#User Registration - allow role setup (student/teacher), create username and password
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password or not role:
            return render_template('register_user.html', error="All fields are required")

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template('register_user.html', error="Username already exists")
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register_user.html')




# User Login - allow student or teacher to enter created username and password
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user or not check_password_hash(user[2], password):
            return render_template('login.html', error="Invalid username or password")

        session['user_ID'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]

        if user[3] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('lessons'))

    return render_template('login.html')



# User Logout - takes user back to login page
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))





#F1.2 -- Display Lessons
# Display Lessons
@app.route('/lessons')
def lessons():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Lessons.*, Quiz.quiz_ID FROM Lessons LEFT JOIN Quiz ON Lessons.lesson_ID = Quiz.lesson_ID")
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
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        lesson_id = request.form.get('lesson_id')  # ← get lesson_id from form

        if not title:
            cursor.execute("SELECT lesson_ID, title FROM Lessons")
            lessons = cursor.fetchall()
            conn.close()
            return render_template('create_quiz.html', error="Quiz title is required", lessons=lessons)

        if 'question_1' not in request.form:
            cursor.execute("SELECT lesson_ID, title FROM Lessons")
            lessons = cursor.fetchall()
            conn.close()
            return render_template('create_quiz.html', error="At least one question is required", lessons=lessons)

        # ← now inserting lesson_id too
        cursor.execute("INSERT INTO Quiz (lesson_ID, title) VALUES (?, ?)", (lesson_id, title,))
        quiz_ID = cursor.lastrowid

        i = 1
        while f'question_{i}' in request.form:
            question_text = request.form[f'question_{i}'].strip()
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
        return redirect(url_for('lessons'))

    # GET request — load lessons for dropdown
    cursor.execute("SELECT lesson_ID, title FROM Lessons")
    lessons = cursor.fetchall()
    conn.close()
    return render_template('create_quiz.html', lessons=lessons)






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






#F5.1 Student Progress & Dashboard
@app.route('/progress')
def progress():
     if not session.get('user_ID'):
        return redirect(url_for('login'))
     
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







#F6.1 Teacher Dashboard
@app.route('/teacher/dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('lessons'))

    conn = get_db()
    cursor = conn.cursor()

    # All students listed and their scores 
    cursor.execute("""
        SELECT Users.user_ID, Users.username, 
               COUNT(Quiz_Results.result_ID) as quizzes_taken,
               AVG(Quiz_Results.score) as avg_score
        FROM Users
        LEFT JOIN Quiz_Results ON Users.user_ID = Quiz_Results.user_ID
        WHERE Users.role = 'student'
        GROUP BY Users.user_ID
    """)
    students = cursor.fetchall()

    # All quizzes and average scores
    cursor.execute("""
        SELECT Quiz.title,
               COUNT(Quiz_Results.result_ID) as times_taken,
               AVG(Quiz_Results.score) as avg_score
        FROM Quiz
        LEFT JOIN Quiz_Results ON Quiz.quiz_ID = Quiz_Results.quiz_ID
        GROUP BY Quiz.quiz_ID
    """)
    quizzes = cursor.fetchall()

    conn.close()
    return render_template('teacher_dashboard.html', students=students, quizzes=quizzes)





# F6.2 Select and View Single Student Progress
@app.route('/teacher/student/<int:user_ID>')
def view_student(user_ID):
    if session.get('role') != 'teacher':
        return redirect(url_for('lessons'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE user_ID=?", (user_ID,))
    student = cursor.fetchone()

    cursor.execute("""
        SELECT Quiz.title, Quiz_Results.score, Quiz_Results.completion_date
        FROM Quiz_Results
        JOIN Quiz ON Quiz_Results.quiz_ID = Quiz.quiz_ID
        WHERE Quiz_Results.user_ID = ?
        ORDER BY Quiz_Results.completion_date DESC
    """, (user_ID,))
    results = cursor.fetchall()

    conn.close()
    return render_template('view_student_progress.html', student=student, results=results)



#home page of jannah journey
@app.route('/')
def home():
    return redirect('/lessons')


if __name__ == '__main__':
    app.run(debug=True)

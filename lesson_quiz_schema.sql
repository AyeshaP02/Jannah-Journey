 -- Author: Ayesha Patel
 -- Date: 3/26/26
 
 -- Users Table
 CREATE TABLE IF NOT EXISTS Users (
    user_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(250) NOT NULL,
    role VARCHAR(20) NOT NULL -- 'could be teacher or student'
);

-- Lessons Table
-- Stores all lesson content
CREATE TABLE IF NOT EXISTS Lessons (
    lesson_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(250) NOT NULL,
    topic VARCHAR(200),
    content TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Quizzes Table
-- Will handle quizzes, questions, and answer choices
CREATE TABLE IF NOT EXISTS Quiz (
    quiz_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_ID INTEGER,
    title VARCHAR(250) NOT NULL,
    FOREIGN KEY (lesson_ID) REFERENCES Lessons(lesson_ID) ON DELETE CASCADE
);

-- Questions Table
-- Each question belongs to one quiz (1 - many relationship) 

CREATE TABLE IF NOT EXISTS Questions (
    question_ID  INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_ID INTEGER,
    question_text TEXT NOT NULL,
    FOREIGN KEY (quiz_ID) REFERENCES Quiz(quiz_ID) ON DELETE CASCADE
);

-- Answer Choices Table
-- Stores Multiple Choice answers
CREATE TABLE IF NOT EXISTS Choices (
    choice_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    question_ID INTEGER,
    choice_text VARCHAR(250) NOT NULL,
    is_correct INTEGER DEFAULT 0,
    FOREIGN KEY (question_ID) REFERENCES Questions(question_ID) ON DELETE CASCADE
);

-- Quiz Results Table
CREATE TABLE IF NOT EXISTS Quiz_Results (
    result_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    user_ID INTEGER,
    quiz_ID INTEGER,
    score INTEGER,
    completion_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_ID) REFERENCES Users(user_ID),
    FOREIGN KEY (quiz_ID) REFERENCES Quiz (quiz_ID)
);


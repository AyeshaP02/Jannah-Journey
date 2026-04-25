Test Plans Documentation - What I found

**All related screenshots are available in the Excel Workbook.**

F1.T1 - I ran the file seed.py which executed the lesson_quiz_schema.sql tables. 
This was verified using the checck.py file. I was able to verify that the Lessons table was created with the correct colums and that all of them exist.
the sample records inserted in seed.py retrieved without any errors.

F1.T2 - I navigated to the lessons page. This helped me verify that all 3 lessons in my seed.py displayed. 
The was successful as all data matched what was in the database, and the page loaded without any errors. 

F1.T3 - I tested the edit lesson button and edit_lesson.html. I selected an existing lesson and tried to modify
the content. I then submitted the update and reloaded the lessons page. Successfully the changes were saved and reflected in the the new changes.

F1.T4 - I then tested the delete button. I selected a lesson and clicked 'Delete' and pop up appeared to confirm deletion. Successfully no error was dsiplayed, the lesson/record was removed from the database.

F2.T1 - Next I tested Feature 2. I navigated to the create new lesson page. I verified that all the text fields accepted input(title, topic, and content). Successfully all the fields on this page were visible, and text inputs were accepted  correctly.

F2.T2 - I entered valid lesson content and submitted the form using the save lesson button. I then reloaded the lessons page. Successfully the lesson was saved in the database and the new lesson appeared in the lesson library list. 
I then left all required fields empty and submitted the form. Successfully an error dsiplayed asking the user to enter a title and content. Input validation prevented submission of the form. 

F3.T1 - I tested feature 3- Quiz Creation. I ran the check.py file to verify all tables from the lesson_quiz_schema exist. This verified there is a proper relationship between the quiz and quiz results tables. Successfully the tables were created and exist. All relationships are valid, no errors occur. 

F3.T2 - Next i navigated to the quiz creation page. I entered the quiz title and questions and selected which was the correct answer choice. Successfully accepted all inputs and the UI behaves correctly.

F3.T3 - Next I submitted the quiz form and checked the database saved the tables. I also verified the questions and answers were saved correctly. Successfully the data is stored correctly, and the questions are linked to the answers and there are no errors.  
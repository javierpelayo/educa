# Educa is a simple learning management system (LMS) that is built via the Flask Framework.

# For Students
It features a dashboard where students can add courses via a course code sent by them from an instructor. Each student is free to do assignments, take exams/quizzes and turn in assignments via the upload feature. Each course also contains a page where all lectures are posted. Students may also view their grades for any recent assignments that they have done. Most assignments that have questions added to them via the field form are graded right away. Whereas a file upload will be graded when an instructor gets to it.

# For Instructors
Any person that decides to sign up as an instructor is free to create new courses. When prompted to create a new course you are free to decide the name, subject, passcode and the amount of points assigned to the course. Instructors can create a syllabus, assignments and can include lectures(from an outside video source). When creating assignments instructors can choose the type of assignment it will be. Depending on the type of assignment, you can add questions and even the correct answer for that particular question. Each question has the choice to be be multiple choice, an input or a paragraph. Each instrucor in the course has the ability to grade a students assignments via the Grades/Students tab which also shows the assignments that a particular student has done.

# Inbox/Messaging
The inbox feature comes with the ability to contact any students or instructors in any course that you have joined and also comes with the ability to create groups.

# Misc/Technologies
Educa relies on PostgreSQL for its database management and SQLAlchemy for its object-relational management, the Postgres server credentials can be configured inside of app/config.py

This project is unfinished for the meantime but serves as an example of the usage of CRUD with the following technologies:

Bootstrap, HTML/CSS & JS, Python, Flask/SQLAlchemy/Blueprints & PostgreSQL along with other libraries that rely on the Flask Framework.

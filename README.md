# Educa
Simple learning management system (LMS) built via the Flask Framework.

Educa gives instructors the ability to create courses which allows them to keep track of grades & assignments for their students as well as keep an open communication channel with them using the inbox feature.

Demo: https://educa-lms.herokuapp.com

An account must be registered to access the dashboard.

Note that instructor accounts are limited to creating four courses and twenty assignments per course. File upload for instruction assignments & for profile pictures is also disabled as this is a demo.

# Student
When logging in as a student, there will be a tab to access the dashboard. Clicking this tab gives access to the profile, courses, deadlines and inbox features for the student account. When accessing the profile page, a student can update their name, email, biography and as well as their profile picture. The profile page also shows a list of assignments that the student has completed as well as the courses that they are in. The courses tab is the most important feature since it keeps track of all of the courses that a student is in. In order to join a course a passcode as well as the course id or CRN(Course Registration Number) will be needed, these will be emailed to them by their instructor or given to them in a physical or online lecture. Once the course has been added, a student will have access to the syllabus, assignments, their grades and a list of students that are also in the course. Going over the deadline tab gives the student access to a list of assignments that have yet to be completed for all of their courses. Lastly, the inbox feature allows students to start a conversation with either another student in their course or the instructor for said course, it is also possible to create a group chat with multiple people, which can help in order to create study sessions.

# How to add a course as a student:

Look for the blue add icon on the courses page

<img width="480" alt="Screen Shot 2022-04-01 at 12 00 16 PM" src="https://user-images.githubusercontent.com/48416882/173207970-d1678926-1011-4b2e-b153-2546defbe506.png">

Enter the course ID and passcode given by your instructor.

<img width="480" alt="adding a course" src="https://user-images.githubusercontent.com/48416882/172786378-7ddf9514-f407-4145-bd4e-4b5b62ebf8df.png">

# Instructors

Similarly to a student account, instructors are given access to the dashboard, along with the same features that a student has. The only difference is that instructors have the ability to create new courses, create new assignments and grade the students that have joined their course. Instructors are given ful reign over the course and can update their syllabus accordingly as well as edit grades as they see fit even long after a certain assignment has been submitted. They have the ability to drop students from the course and can also delete the course itself.

# How to create a course:

Clicking the same blue plus icon on the courses page similarly to a student account, you will be met with a new course pop up.

<img width="480" alt="Screen Shot 2022-06-09 at 1 55 51 AM" src="https://user-images.githubusercontent.com/48416882/173208188-791684d2-3d52-482f-92be-efd8a64d5a8a.png">

The max points corresponds to the max number of points that a student can get, for example if the max points is 800, then if a student completes all assignments totalling to the max points then they would have 100% which is an A in the course. 

# How to create an assignment:

Click on the new assignment button

<img width="480" alt="Screen Shot 2022-06-11 at 4 48 24 PM" src="https://user-images.githubusercontent.com/48416882/173208490-29d6182e-1001-4616-bb9e-78dbbd4e4cba.png">

Most importantly when creating the assignment you will be given the option to choose the type of assignment that this will be, every type of assignment is given the option to add questions to be answered except for the instructions option.

<img width="480" alt="Screen Shot 2022-06-09 at 1 56 09 AM" src="https://user-images.githubusercontent.com/48416882/173208496-f321d3a3-2088-4ed3-8bd9-89d214ddba2b.png">

When adding a question you are given the option to input the question title, the question itself, the correct answer and the number of points that the question is worth.

<img width="480" alt="Screen Shot 2022-06-09 at 1 58 12 AM" src="https://user-images.githubusercontent.com/48416882/173208559-be6fb18e-ef90-4fe2-ac58-f54ba6361c17.png">

You are also given the choice of the question being answered as an input, multiple choice or paragraph.

<img width="480" alt="Screen Shot 2022-06-11 at 4 54 54 PM" src="https://user-images.githubusercontent.com/48416882/173208650-5787ca51-9937-4ab7-95d2-ee7b436b87ff.png">

# How to initiate a conversation using the inbox feature

Click the pencil draft icon and a new conversation prompt will appear.

<img width="480" alt="Screen Shot 2022-04-01 at 12 12 16 PM" src="https://user-images.githubusercontent.com/48416882/173217577-6932ae88-81fa-47f3-8984-7aa5b484219d.png">

Write a title for the conversation and use the search feature to find classmates or the instructor for the course that is selected

<img width="480" alt="Screen Shot 2022-04-01 at 12 13 01 PM" src="https://user-images.githubusercontent.com/48416882/173217609-2cf417f0-47b4-49c3-9315-3b9a0f9ded98.png">

After you have finished the message you can hit send and you will be redirected to the conversation.

<img width="480" alt="Screen Shot 2022-04-01 at 12 14 20 PM" src="https://user-images.githubusercontent.com/48416882/173217763-9c104704-c6c5-48f7-8f1d-6fead973de95.png">

# I want to create my own instance of this application

----

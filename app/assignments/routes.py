from flask import Blueprint

assignments = Blueprint("assignments", __name__)

@assignments.route('/dashboard/courses/<int:course_id>/assignments', methods=['GET'])
@login_required
@course_auth
def assignments(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    assignments = sorted(assignments, key=lambda a: a.duedate_time)
    user_assignments = []

    for a in assignments:
        user_assignment = User_Assignment.query.filter_by(user_id=current_user.id, assignment_id=a.id).all()
        if user_assignment:
            user_assignment.sort(key=lambda a:a.created_time)
            user_assignments.append(user_assignment[-1])
        else:
            user_assignments.append(0)

    if request.method == "GET":
        return render_template('assignments.html',
                                course=course,
                                assignments=assignments,
                                user_assignments=user_assignments,
                                current_time=time(),
                                title=str(course.title) + " - Assignments")

@assignments.route('/dashboard/courses/<int:course_id>/assignments/new', methods=["GET", "POST"])
@login_required
@course_auth
@teacher_auth
def new_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first()
    assignmentform = AssignmentForm()
    errors = {}

    request_form = request.form.to_dict()

    if "ajax" in request_form and request.method == "POST":
        return new_assignment_error_handler(assignmentform, request_form)
    if request.method == "POST":
        errors = new_assignment_error_handler(assignmentform, request_form)
        if errors:
            flash("There was an error in creating that assignment.", "danger")
            return redirect(url_for('new_assignment', course_id=course.id))

        questions = {}
        options = {}
        q_ids = []
        question_option_ids = []
        question_amt = 0

        # separate the questions from the options
        for key, value in request_form.items():
            if "question_option" in key:
                options[key] = value
            elif "question_" in key:
                questions[key] = value

        # Split the POST question variables to just be question ids
        for key, value in questions.items():
            question_ids = key.split("_")
            question_id = question_ids[2]
            if question_id not in q_ids:
                q_ids.append(question_id)

        # Split the POST option variables to just be question ids with option ids
        for key, value in options.items():
            qu_op_ids = key.split("_")
            q_id = qu_op_ids[2]
            o_id = qu_op_ids[3]

            question_option_ids.append((q_id, o_id))

        q_ids.sort()
        question_amt = len(q_ids)

        date_input = assignmentform.date_input.data.strftime('%m/%d/%Y').split("/")
        hour = int(assignmentform.hour.data)
        minute = int(assignmentform.minute.data)
        month = int(date_input[0])
        day = int(date_input[1])
        year = int(date_input[2])

        datetime_object = datetime(year, month, day, hour, minute)

        duedate_time = datetime.timestamp(datetime_object)
        duedate_ctime = datetime.fromtimestamp(duedate_time).isoformat() + "Z"

        assignment = Assignment(course_id=course.id,
                                points=assignmentform.points.data,
                                title=assignmentform.title.data,
                                content=assignmentform.content.data,
                                type=assignmentform.type.data,
                                tries=assignmentform.tries.data,
                                duedate_time=duedate_time,
                                duedate_ctime=duedate_ctime)
        db.session.add(assignment)
        db.session.commit()

        # CREATE each question for the assignment
        for x in range(question_amt):
            question = Question(assignment_id=assignment.id,
                                title=questions['question_title_' + str(x)],
                                content=questions['question_content_' + str(x)],
                                answer=questions['question_answer_' + str(x)],
                                points=questions['question_points_' + str(x)],
                                type=questions['question_type_' + str(x)])

            db.session.add(question)
            db.session.commit()

            # CREATE each option for that question
            for key, value in question_option_ids:
                if key == str(x):
                    option = Option(question_id=question.id,
                                    content=options["question_option_" + key + "_" + value])
                    db.session.add(option)
                    db.session.commit()

        flash("Assignment was created successfully!", "success")
        return redirect(url_for("assignments", course_id=course.id))

    elif request.method == "GET":
        return render_template('new_assignment.html',
                                course=course,
                                assignmentform=assignmentform,
                                title=str(course.title) + " - New Assignment")

# NO CSRF
@assignments.route('/dashboard/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@course_auth
def assignment(course_id, assignment_id):

    file = request.files.get("file")
    upload = request.form.get("upload")

    redo = request.args.get("redo")
    delete = request.form.get("delete")
    request_form = request.form.to_dict()

    course = Course.query.filter_by(id=course_id).first()
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    user_assignments = User_Assignment.query.filter_by(user_id=current_user.id, assignment_id=assignment.id).all()
    questions = Question.query.filter_by(assignment_id=assignment.id).all()
    options_dict = {}

    questions.sort(key=lambda q:q.id)
    user_assignments.sort(key=lambda a:a.points)
    tries = len(user_assignments)

    if user_assignments:
        user_assignment = user_assignments[-1]
        tries = user_assignment.tries
    else:
        user_assignment = ''

    # get all options for each question
    for question in questions:
        options = question.options
        options_dict[str(question.id)] = options

    if request.method == "POST" and upload and assignment.type == "Instructions":
        if tries < assignment.tries:
            course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()
            filename = save_assignment(file)

            if filename:
                calculate_grade(course_user, assignment, 0)
                for ua in user_assignments:
                    delete_assignment(ua.filename)
                    db.session.delete(ua)

                user_assignment = User_Assignment(user_id=current_user.id,
                                                assignment_id=assignment.id,
                                                filename=filename,
                                                tries=tries+1,
                                                points=0,
                                                type=assignment.type)

                db.session.add(user_assignment)
                db.session.commit()
                flash("Assignment has been successfully submitted.", "success")
                return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))
            else:
                flash("That file type is not allowed.", "warning")
                return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))
        else:
            flash("You have already reached your max tries.", "warning")
            return redirect(url_for('assignments', course_id=course.id))


        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif current_user.id == course.teacher_id and request.method == "POST" and delete:
        course_assignments = Assignment.query.filter_by(course_id=course.id).all()
        course_users = Course_User.query.filter_by(course_id=course.id).all()
        total_assignment_points = 0

        # get the total point count for assignments in course
        for course_assignment in course_assignments:
            total_assignment_points += course_assignment.points

        # for every user in the course delete assignments that
        # they turned in for this assignment & reflect the change
        # to their grade
        for course_user in course_users:
            turned_in_assignments = User_Assignment.query.filter_by(user_id=course_user.user_id, assignment_id=assignment.id).all()

            if turned_in_assignments:
                turned_in_assignments.sort(key=lambda a:a.created_time)
                student_assignment = turned_in_assignments[-1]

                assignments_done = json.loads(course_user.assignments_done)
                del assignments_done[str(assignment.id)]
                course_user.assignments_done = json.dumps(assignments_done)

                course_user.points -= student_assignment.points

                try:
                    leftover_points = course_user.points/(total_assignment_points - assignment.points)
                except ZeroDivisionError:
                    leftover_points = 0

                course_user.grade = '{:.2%}'.format(leftover_points)

        # deletion of assignments cascades to questions, options and user_assignments
        db.session.delete(assignment)
        db.session.commit()

        flash('Assignment was deleted successfully!', 'success')
        return redirect(url_for("assignments", course_id=course.id))
    if "ajax" in request_form and request.method == "POST":
        return assignment_error_handler(request_form)
    elif request.method == "POST" and current_user.profession == "Student" and tries < assignment.tries:

        errors = assignment_error_handler(request_form)
        if errors:
            flash("There was an error in submitting this assignment.", "danger")
            return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))

        course_user = Course_User.query.filter_by(user_id=current_user.id, course_id=course.id).first()
        total_assignment_points = 0
        answers = []
        points = 0

        for key, value in request_form.items():
            if "question_" in key:
                answers.append(value)

        for i in range(len(answers)):
            if questions[i].answer == answers[i]:
                points += questions[i].points

        if assignment.points == points:
            tries = assignment.tries
        else:
            tries += 1

        calculate_grade(course_user, assignment, points)

        user_assignment = User_Assignment(user_id=current_user.id,
                                        assignment_id=assignment.id,
                                        filename="",
                                        answers=answers,
                                        points=points,
                                        tries=tries,
                                        type=assignment.type)

        db.session.add(user_assignment)
        db.session.commit()

        flash("Assignment turned in!", "success")
        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif request.method == "POST":
        flash("You can no longer redo this assignment.", "danger")
        return redirect(url_for("assignment", course_id=course.id, assignment_id=assignment.id))
    elif request.method == "GET":
        return render_template('assignment.html',
                                course=course,
                                assignment=assignment,
                                current_time=time(),
                                user_assignment=user_assignment,
                                questions=questions,
                                options_dict=options_dict,
                                redo=redo,
                                tries=tries,
                                title=course.title + " - " + assignment.title)
from flask import current_app
import magic
import secrets
import os

def assignment_error_handler(request_form):
    errors = {}
    for key, value in request_form.items():
        if "question_" in key and value == "":
            errors[key] = "This question requires an answer."

    return errors

def new_assignment_error_handler(assignmentform, request_form):
    errors = {}
    assignmentform.validate()
    question_total_points = 0

    for key, value in assignmentform.errors.items():
        if key == "date_input":
            errors[key] = "Not a valid date value. ex: 01/25/2020"
        else:
            errors[key] = value[0]
    for key, value in request_form.items():
        if "qOption_" in key and value == "":
            errors[key] = "This field is required."
        elif "question_points" in key:
            try:
                question_total_points += int(value)
            except ValueError:
                errors[key] = "Not a valid integer value."
        elif "question_answer" not in key and "question_" in key and value == "":
            errors[key] = "This field is required."

    try:
        a_points = int(request_form["points"])
    except ValueError:
        a_points = 0

    if question_total_points > a_points:
        for key, value in request_form.items():
            if "question_points" in key:
                errors[key] = f"Total question points exceeds assignment points: {a_points}"

    return errors

def save_assignment(file):
    # random_hex = secrets.token_hex(8)
    # _, f_ext = os.path.splitext(file.filename)
    # fn = random_hex + f_ext
    # file_path = os.path.join(current_app.root_path,
    #                             'static/assignments',
    #                             fn)
    # file.save(file_path)

    # accepted_types = ["PDF", "PNG", "JPG", "JPEG"]
    # with open(file_path, 'rb') as f:
    #     type = magic.from_buffer(f.read(2048))
    # if any(at in type for at in accepted_types):
    #   return fn

    # os.remove(file_path)
    # return
    return False

def delete_assignment(fn):
    file_path = os.path.join(current_app.root_path,
                                'static/assignments',
                                fn)
    os.remove(file_path)
from flask import (Blueprint, request, redirect, render_template,
                    url_for)
from flask_login import login_required, current_user
from app.inbox.utils import inbox_info, searched_users
from app.inbox.forms import NewConversationForm, NewMessageForm
from app.models import (Conversation_User, Message, User_Account,
                        Conversation)
from app.filters import autoversion
from app import db, limiter
import json

inbox_ = Blueprint("inbox", __name__)

# NO CSRF
@inbox_.route('/dashboard/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    conversation_snippets = inbox_info()

    delete = request.form.get("delete")

    if request.method == "POST" and delete:
        request_form = request.form.to_dict()
        convos_del = [Conversation_User.query.filter_by(user_id=current_user.id, conversation_id=int(value)).first() for key, value in request_form.items() if "convo_" in key]

        for convo_user in convos_del:
            message = Message(conversation_id=convo_user.conversation_id,
                        user_id=current_user.id,
                        content=f"{current_user.first_name} {current_user.last_name} has left this conversation.",
                        msg_type="left")
            db.session.add(message)

        for convo in convos_del:
            db.session.delete(convo)

        db.session.commit()

        return redirect(url_for("inbox.inbox"))

    return render_template("conversation.html",
                            conversation_snippets=conversation_snippets,
                            title="Inbox")

@inbox_.route('/dashboard/inbox/conversation/new/search', methods=['GET'])
@login_required
@limiter.exempt
def get_recipients():
    request_args = request.args.to_dict()
    if request.method == "GET":
        return searched_users(request_args['name'], request_args['course_id'])

@inbox_.route('/dashboard/inbox/conversation/new', methods=['GET', 'POST'])
@login_required
def new_conversation():
    conversation_snippets = inbox_info()
    recipient = request.args.get("recipient_id")
    if recipient:
        recipient = User_Account.query.filter_by(id=int(recipient)).first()
    request_form = request.form.to_dict()

    if request.method == "POST":
        recipients = [{key: value} for key, value in request_form.items() if "recipient_" in key]
        form = NewConversationForm(recipients=recipients)

        if form.validate_on_submit():
            conversation = Conversation(title=form.title.data)
            db.session.add(conversation)
            db.session.commit()

            conversation_user = Conversation_User(user_id=current_user.id, conversation_id=conversation.id, read=True)

            for recipient_id in set(form.recipients.data):
                if current_user.id != int(recipient_id):
                    conversation_recipient = Conversation_User(user_id=int(recipient_id), conversation_id=conversation.id)
                    db.session.add(conversation_recipient)

            msg = Message(conversation_id=conversation.id,
                                user_id=current_user.id,
                                content=form.message.data)
            
            db.session.add(conversation_user)
            db.session.add(msg)
            db.session.commit()

            return redirect(url_for("inbox.conversation", convo_id=conversation.id))
        else:
            return redirect(url_for("inbox.new_conversation"))
    elif request.method == "GET":
        form = NewConversationForm()
        return render_template("new_conversation.html",
                            conversation_snippets=conversation_snippets,
                            recipient=recipient,
                            form=form,
                            title="New Conversation")

@inbox_.route('/dashboard/inbox/conversation/<int:convo_id>/update', methods=['GET'])
@login_required
@limiter.exempt
def update_messages(convo_id):
    conversation = Conversation.query.filter_by(id=convo_id).first()
    messages = conversation.messages
    update_msg = []
    msg_timestamp = float(request.args.get('timestamp'))
    top = request.args.get('top')

    for msg in messages:
        if top == "true":
            if msg.created_time < msg_timestamp and len(update_msg) < 10:
                update_msg.append(msg.rendering_dict())
        else:
            if msg.created_time > msg_timestamp:
                update_msg.append(msg.rendering_dict())

    if top == "true":
        update_msg = sorted(update_msg, key= lambda d: d.get("timestamp"))
    else:
        update_msg = sorted(update_msg, key= lambda d: d.get("timestamp"), reverse=True)
    
    return json.dumps(update_msg)

@inbox_.route('/dashboard/inbox/conversation/<int:convo_id>', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def conversation(convo_id):

    user_convo = Conversation_User.query.filter_by(user_id=current_user.id, conversation_id=convo_id).first()
    user_convo.read = True
    db.session.commit()

    conversation_snippets = inbox_info()
    conversation = Conversation.query.filter_by(id=convo_id).first()

    messages = conversation.messages
    if len(messages) > 10:
        messages = messages[-10:]

    form = NewMessageForm()

    if request.method == "POST" and form.validate_on_submit():
        message = Message(conversation_id=convo_id,
                            user_id=current_user.id,
                            content=form.message.data)

        conversation_users = Conversation_User.query.filter_by(conversation_id=convo_id).all()
        for convo_user in conversation_users:
            if convo_user.user_id != current_user.id:
                convo_user.read = False

        db.session.add(message)
        db.session.commit()

        return redirect(url_for("inbox.conversation", convo_id=convo_id))
    return render_template("conversation.html",
                            conversation=conversation,
                            messages=messages,
                            conversation_snippets=conversation_snippets,
                            form=form,
                            title="Conversation")
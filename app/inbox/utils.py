
def inbox_info():
    conversations = current_user.conversations
    conversations.sort(key=lambda c:c.conversation_id, reverse=True)
    convos = []

    if conversations:
        # fix here
        for i in range(len(conversations)):
            users = []

            for convo_user in conversations[i].conversation.conversation_users:
                users.append(convo_user.user)

            users = ", ".join([user.first_name for user in users])
            msg = Message.query.filter_by(conversation_id=conversations[i].conversation_id).order_by(Message.created_time).all()[-1]

            convos.append({"names": users, "msg": msg.content, "date": msg.created_ctime, "conversation_id": conversations[i].conversation_id, "read": conversations[i].read})

    return convos

def searched_users(name, course_id):
    name = name.title().split(" ")
    first_name = name[0]
    if len(name) > 1:
        last_name = name[1]
    search_match = []
    results_parsed = {}

    search_all = User_Account.query.filter(User_Account.first_name.startswith(first_name)).all()

    for user in search_all:
        if user.profession == "Student":
            search_match += [user for c in user.classes if c.course_id == int(course_id)]
        else:
            search_match += [user for c in user.courses if c.id == int(course_id)]

    for user in search_match:
        if current_user.id != user.id:
            if user.profession == "Student":
                results_parsed[f"{user.first_name} {user.last_name} #{user.id}"] = str(user.id)
            else:
                results_parsed[f"{user.first_name} {user.last_name} - Teacher"] = str(user.id)

    return results_parsed
from firebase_connection import firebase_ref


def updateRanking(uid):
    top5 = firebase_ref.getRef().child("top5").get()
    user = firebase_ref.getRef().child("users").child(uid).get()
    users_points = user.get("total_points")
    insert_index = -1
    for i in range(len(top5)):
        current = top5[i]
        if current.get("total_points") < users_points:
            insert_index = i
            break

    if insert_index != -1:
        for i in range(4, insert_index):
            better_user = firebase_ref.getRef().child("top5").child(i-1).get()
            firebase_ref.getRef().child("top5").child(i).set(better_user)

        data = {
            'nick': user.get("nick"),
            'no_played': user.get("no_played"),
            'no_won': user.get("no_won"),
            'total_points' : users_points
        }
        firebase_ref.getRef().child("top5").child(str(insert_index)).set(data)


def getRanking():
    ranking = firebase_ref.getRef().child("top5").get()
    parsed = []
    for user in ranking:
        parsed.append([user.get('nick'), user.get('total_points')])
    return parsed

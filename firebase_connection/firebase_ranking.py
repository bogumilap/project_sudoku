from firebase_connection import firebase_ref


def update_ranking(uid):
    top5 = firebase_ref.get_db_reference().child("top5").get()
    user = firebase_ref.get_db_reference().child("users").child(uid).get()
    users_points = user.get("total_points")
    lowest_ranking = min(top5, key=lambda x: x.get("total_points"))

    if lowest_ranking["total_points"] < users_points:
        data = {
            'nick': user.get("nick"),
            'no_played': user.get("no_played"),
            'no_won': user.get("no_won"),
            'total_points': users_points
        }
        insert_index = top5.index(lowest_ranking)
        firebase_ref.get_db_reference().child("top5").child(str(insert_index)).set(data)


def get_ranking():
    ranking = firebase_ref.get_db_reference().child("top5").get()
    parsed = [(user.get('nick'), user.get('total_points')) for user in ranking]
    parsed.sort(key=lambda x: x[1], reverse=True)
    return parsed

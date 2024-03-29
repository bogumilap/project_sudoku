from firebase_connection import firebase_ref


def add_user(uid, nick, email):  # adding new user to 'users' collection in firebase
    data = {
        'email': email,
        'nick': nick,
        'no_played': 0,
        'no_won': 0,
        'total_points': 0
    }
    firebase_ref.get_db_reference().child('users').child(str(uid)).set(data)



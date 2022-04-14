from firebase_connection import firebase_ref

def addUser(uid, nick, email):  # adding new user to 'users' collection in firebase
    data = {
        'email': email,
        'nick': nick,
        'no_played': 0,
        'no_won': 0,
        'total_points': 0
    }
    firebase_ref.getRef().child('users').child(str(uid)).set(data)


# initializing ranking
top5 = {
    '0': {
        'nick': 'user0',
        'total_points': 0,
        'no_won': 0,
        'no_played': 0
    },
    '1': {
        'nick': 'user1',
        'total_points': 0,
        'no_won': 0,
        'no_played': 0
    },
    '2': {
        'nick': 'user2',
        'total_points': 0,
        'no_won': 0,
        'no_played': 0
    },
    '3': {
        'nick': 'user3',
        'total_points': 0,
        'no_won': 0,
        'no_played': 0
    },
    '4': {
        'nick': 'user4',
        'total_points': 0,
        'no_won': 0,
        'no_played': 0
    }
}

firebase_ref.getRef().child('top5').set(top5)


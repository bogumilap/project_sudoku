import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("../firebase_connection/sudoku-ecca5-firebase-adminsdk-39oik-b57bb08c6c.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sudoku-ecca5-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference('/')


def addUser(uid, nick, email):  # adding new user to 'users' collection in firebase
    data = {
        'email': email,
        'nick': nick,
        'no_played': 0,
        'no_won': 0,
        'total_points': 0
    }
    ref.child('users').child(str(uid)).set(data)


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

ref.child('top5').set(top5)


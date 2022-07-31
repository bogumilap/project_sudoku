from firebase_connection import firebase_insert

import pyrebase
from requests import HTTPError
from firebase_connection import firebase_ref

firebaseConfig = {
    "apiKey": "AIzaSyBxMCsRr5oTMtonLTujyKYpxFrYeJkqHks",
    "authDomain": "sudoku-ecca5.firebaseapp.com",
    "databaseURL": "https://sudoku-ecca5-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "sudoku-ecca5",
    "storageBucket": "sudoku-ecca5.appspot.com",
    "messagingSenderId": "1072697919160",
    "appId": "1:1072697919160:web:b099ca904c9e074869d64d",
    "measurementId": "G-M2K20GH8DJ"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
uid = None


# log in to account
def login(email_, password_):
    global uid
    try:
        user = auth.sign_in_with_email_and_password(email_, password_)
        uid = user.get('localId')
        return user.get('localId')
    except HTTPError:
        return -1


# sign up to database
def signup(nick, email, password):
    global uid
    try:
        user = auth.create_user_with_email_and_password(email, password)
        firebase_insert.add_user(user.get('localId'), nick, email)  # creating position in 'users' collection in db
        print(user.get('localId'))
        firebase_ref.get_db_reference().child('history').push(user.get('localId'))  # creating document for user's history of play
        uid = user.get('localId')
        return user.get('localId')
    except HTTPError:
        return -1


def get_uid():
    return uid


def get_current_nick():
    return firebase_ref.get_db_reference().child('users').child(uid).child('nick').get()

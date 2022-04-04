import firebase_admin
from firebase_admin import credentials
from getpass import getpass
from firebase_connection import firebase_insert

import pyrebase
from requests import HTTPError

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


# log in to account
def login(email_, password_):
    try:
        login = auth.sign_in_with_email_and_password(email_, password_)
    except HTTPError:
        return -1


# sign up to database
def signup(nick, email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        firebase_insert.addUser(user.get('localId'), nick, email)  # creating position in 'users' collection in db
    except HTTPError:
        return -1

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("../firebase_connection/sudoku-ecca5-firebase-adminsdk-39oik-b57bb08c6c.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sudoku-ecca5-default-rtdb.europe-west1.firebasedatabase.app/'
})

ref = db.reference('/')


def getRef():
    return ref

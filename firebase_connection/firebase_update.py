from firebase import firebase

firebase = firebase.FirebaseApplication("https://sudoku-ecca5-default-rtdb.europe-west1.firebasedatabase.app/", None)

firebase.put('/top5/0', 'no_played', 2)
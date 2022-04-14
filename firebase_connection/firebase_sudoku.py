from firebase_connection import firebase_ref


def getUnsolved(id):
    return firebase_ref.getRef().child('unsolved_sudoku').child(str(id)).child("numbers").get()


def getSolved(id):
    return firebase_ref.getRef().child('solved_sudoku').child(str(id)).child("numbers").get()


def getLevel(id):
    return firebase_ref.getRef().child('solved_sudoku').child(str(id)).child("level").get()


def getUserSolution(uid, sudoku_id):
    history = firebase_ref.getRef().child('history').child(str(uid))

    if history.child(str(sudoku_id)) is None:  # game needs to be added to user's game history
        data = {
            'numbers': [[0 for _ in range(9)] for _ in range(9)],
            'time': (0, 0),
            'game points': 0,
            'used hints': 0,
            'used corrections': 0
        }
        history.child(str(sudoku_id)).set(data)

    return history.child(str(sudoku_id)).child('numbers').get()


def updateUserSolution(uid, sudoku_id, x, y, val):
    sudoku = getUserSolution(uid, sudoku_id)
    sudoku[x][y] = val
    return firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child("numbers").set(sudoku)



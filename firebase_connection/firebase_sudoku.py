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
            'game_points': 0,
            'used_hints': 0,
            'used_corrections': 0
        }
        history.child(str(sudoku_id)).set(data)
        no_played = firebase_ref.getRef().child('users').get('no_played')  # update user statistics
        firebase_ref.getRef().child('users').child('no_played').set(no_played+1)

    return history.child(str(sudoku_id)).child('numbers').get()


def updateUserSolution(uid, sudoku_id, x, y, val):  # insert number to user's game history
    sudoku = getUserSolution(uid, sudoku_id)
    sudoku[x][y] = val
    return firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child("numbers").set(sudoku)


def finishGame(uid, sudoku_id):  # update user's statistics and total points
    user_data = firebase_ref.getRef().child('users').child(str(uid))
    no_won = user_data.child('no_won').get()
    total_points = user_data.child('total_points').get()
    game_points = firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('game_points').get()
    user_data.child('no_won').set(no_won + 1)
    user_data.child('total_points').set(total_points + game_points)


def getAllSolvedSudoku():
    return firebase_ref.getRef().child('solved_sudoku').get()


def getSudokuWithLevel(level):
    all_sudoku = getAllSolvedSudoku()
    lvl_sudoku = []
    for i in range(len(all_sudoku)):
        if all_sudoku[i]['level'] == level:
            lvl_sudoku.append(i)
    return lvl_sudoku




from firebase_connection import firebase_ref


def getUnsolved(id):
    return firebase_ref.getRef().child('unsolved_sudoku').child(str(id)).child("numbers").get()


def getSolved(id):
    return firebase_ref.getRef().child('solved_sudoku').child(str(id)).child("numbers").get()


def getLevel(id):
    return firebase_ref.getRef().child('solved_sudoku').child(str(id)).child("level").get()


def getUserSolution(uid, sudoku_id):
    if uid is None:
        return

    history = firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id))

    if history.get() is None:  # game needs to be added to user's game history
        data = {
            'numbers': [[0 for _ in range(9)] for _ in range(9)],
            'time': [0, 0, 0],
            'game_points': 0,
            'used_hints': 0,
            'used_corrections': 0,
            'progress_bar': 0.0
        }
        history.set(data)
        no_played = firebase_ref.getRef().child('users').child(uid).child('no_played').get()  # update user statistics
        firebase_ref.getRef().child('users').child(uid).child('no_played').set(no_played+1)

    return history.child('numbers').get()


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
            lvl_sudoku.append(all_sudoku[i]['id'])
    return lvl_sudoku


def get_hint(id, history_id, square, field):
    num = firebase_ref.getRef().child('solved_sudoku').child(id).child('numbers').child(square).child(field).get()
    firebase_ref.getRef().child('history').child(str(history_id)).child(id).child('numbers').child(square).child(field).set(num)
    return num


def count_hint(id, history_id, square, field):
    def is_repetition_in_row(board, square, field):
        need_squares = [square]
        if square % 3 == 0:
            need_squares.append(square + 1)
            need_squares.append(square + 2)
        elif square % 3 == 1:
            need_squares.append(square - 1)
            need_squares.append(square + 1)
        else:
            need_squares.append(square - 1)
            need_squares.append(square - 2)

        need_fields = [field]
        if field % 3 == 0:
            need_fields.append(field + 1)
            need_fields.append(field + 2)
        elif field % 3 == 1:
            need_fields.append(field - 1)
            need_fields.append(field + 1)
        else:
            need_fields.append(field - 1)
            need_fields.append(field - 2)

        not_repeted = set()

        for i in range(3):
            for j in range(3):
                elem = board.child('numbers').child(need_squares[i]).child(need_fields[j]).get()
                if elem in not_repeted:
                    return True
                if elem != "":
                    not_repeted.add(elem)

        return False

    def is_repetition_in_column(board, square, field):
        need_squares = [square]
        if square // 3 == 0:
            need_squares.append(square + 3)
            need_squares.append(square + 6)
        elif square // 3 == 1:
            need_squares.append(square - 3)
            need_squares.append(square + 3)
        else:
            need_squares.append(square - 3)
            need_squares.append(square - 6)

        need_fields = [field]
        if field // 3 == 0:
            need_fields.append(field + 3)
            need_fields.append(field + 6)
        elif field // 3 == 1:
            need_fields.append(field - 3)
            need_fields.append(field + 3)
        else:
            need_fields.append(field - 3)
            need_fields.append(field - 6)

        not_repeted = set()

        for i in range(3):
            for j in range(3):
                elem = board.child('numbers').child(need_squares[i]).child(need_fields[j]).get()
                if elem in not_repeted:
                    return True
                if elem != "":
                    not_repeted.add(elem)

        return False

    def is_repetition_in_box(board, square):
        not_repeted = set()
        for i in range(9):
            elem = board.child('numbers').child(square).child(i).get()

            if elem in not_repeted:
                return True
            if elem != "":
                not_repeted.add(elem)

        return False

    def is_valid(board):
        for i in range(9):
            for j in range(9):
                return not is_repetition_in_row(board, square, field) and not is_repetition_in_column(board, square, field) and not is_repetition_in_box(board, square)


    board = firebase_ref.getRef().child('history').child(str(history_id)).child(id)

    res = []
    for i in range(9):
        board.child('numbers').child(square).child(field).set(i)
        if is_valid(board):
            res.append(i)

    return res

def update_progress_bar(uid, sudoku_id, value):
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(value)


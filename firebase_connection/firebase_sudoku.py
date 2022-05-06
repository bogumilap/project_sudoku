from firebase_connection import firebase_ref
from firebase_connection.firebase_ranking import updateRanking


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
            'progress_bar': 0.0,
            'database': "",
            'possible': [[[0 for _ in range(9)] for _ in range(9)] for _ in range(9)]
        }
        history.set(data)
        no_played = firebase_ref.getRef().child('users').child(uid).child('no_played').get()  # update user statistics
        firebase_ref.getRef().child('users').child(uid).child('no_played').set(no_played + 1)

    return history.child('numbers').get()


def updateUserSolution(uid, sudoku_id, x, y, val):  # insert number to user's game history
    sudoku = getUserSolution(uid, sudoku_id)
    if sudoku[x][y] != "" and sudoku[x][y] != 0:   # update points
        points = firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child("game_points")
        points.set(points.get() + 50)
    sudoku[x][y] = val
    return firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child("numbers").set(sudoku)


def getUserPossible(uid, sudoku_id, x, y):
    result = firebase_ref.getRef().child("history").child(uid).child(str(sudoku_id)).child("possible").child(str(x)).child(str(y)).get()
    if result.count(0) > 0:
        result.remove(0)
    return str(result)[1:len(str(result))-1]


def updateUserPossible(uid, sudoku_id, x, y, vals):
    v = vals.split(", ")
    firebase_ref.getRef().child("history").child(uid).child(str(sudoku_id)).child("possible").child(str(x)).child(str(y)).set(v)


def finishGame(uid, sudoku_id):  # update user's statistics and total points
    user_data = firebase_ref.getRef().child('users').child(str(uid))
    game_data = firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id))

    no_won = user_data.child('no_won')
    no_won.set(no_won.get() + 1)

    total_points = user_data.child('total_points').get()
    time = game_data.child("time").get()
    seconds = time[0] * 3600 + time[1] * 60 + time[2]
    game_points = game_data.child('game_points').get()
    gained = game_points * getLevel(sudoku_id) * 10 / seconds
    used = game_data.child("used_corrections").get() * 10 + game_data.child("used_hints").get() * 15
    user_data.child('total_points').set(total_points + gained - used)

    updateRanking(uid)


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
    print(square, field)
    num = firebase_ref.getRef().child('solved_sudoku').child(str(id)).child('numbers').child(square).child(field).get()
    firebase_ref.getRef().child('history').child(str(history_id)).child(str(id)).child('numbers').child(square).child(field).set(num)
    return num


def get_count(id, history_id, row_arg, column_arg):
    int_row_arg = int(row_arg)
    int_col_arg = int(column_arg)

    column = [False] * 9
    row = [False] * 9
    box = [False] * 9

    users_sudoku = firebase_ref.getRef().child('history').child(str(history_id)).child(str(id)).child('numbers').get()
    solved_sudoku = firebase_ref.getRef().child('solved_sudoku').child(str(id)).child('numbers').get()
    # column and row
    for i in range(9):
        column_num = users_sudoku[i][int_col_arg]
        row_num = users_sudoku[int_row_arg][i]
        if column_num != "":
            solved_column_num = solved_sudoku[i][int_col_arg]
            if column_num != 0 and int(column_num) == solved_column_num:
                column[solved_column_num-1] = True

        if row_num != "":
            solved_row_num = solved_sudoku[int_row_arg][i]
            if row_num != 0 and int(row_num) == solved_row_num:
                row[solved_row_num-1] = True

    # box
    row_range_begin = int_row_arg // 3
    column_range_begin = int_col_arg // 3
    row_range_end = row_range_begin + 3
    column_range_end = column_range_begin + 3

    for i in range(row_range_begin, row_range_end):
        for j in range(column_range_begin, column_range_end):
            box_num = users_sudoku[i][j]
            if box_num != "":
                solved_box_num = solved_sudoku[i][j]
                if box_num != 0 and int(box_num) == solved_box_num:
                    box[solved_box_num-1] = True

    res = []
    for i in range(9):
        if not row[i] and not column[i] and not box[i]:
            res.append(i+1)

    return res


def update_progress_bar(uid, sudoku_id, value):
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(value)


def reset_game(uid, sudoku_id):
    unsolved_sudoku = firebase_ref.getRef().child('unsolved_sudoku').child(str(sudoku_id)).get()
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).set(unsolved_sudoku)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('database').set("")
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('game_points').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(0)).set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(1)).set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(2)).set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('used_corrections').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('used_hints').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('possible')\
        .set([[[0 for _ in range(9)] for _ in range(9)] for _ in range(9)])



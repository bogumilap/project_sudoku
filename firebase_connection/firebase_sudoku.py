from firebase_connection import firebase_ref
from firebase_connection.firebase_ranking import updateRanking


def getUnsolved(id):
    return firebase_ref.getRef().child('unsolved_sudoku').child(str(id)).child("numbers").get()


def getSolved(id):
    return firebase_ref.getRef().child('solved_sudoku').child(str(id)).child("numbers").get()


def getLevel(id):
    return firebase_ref.getRef().child('solved_sudoku').child(str(id)).child("level").get()


def getUserSolution(uid, sudoku_id, is_multiplayer):
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
            'hints': "",
            'possible': [[[0 for _ in range(9)] for _ in range(9)] for _ in range(9)]
        }
        history.set(data)
        no_played = firebase_ref.getRef().child('users').child(uid).child('no_played').get()  # update user statistics
        if not is_multiplayer:
            firebase_ref.getRef().child('users').child(uid).child('no_played').set(no_played + 1)

    return history.child('numbers').get()


def updateUserSolution(uid, sudoku_id, x, y, val, is_multiplayer):  # insert number to user's game history
    sudoku = getUserSolution(uid, sudoku_id, is_multiplayer)
    print(sudoku[x][y])
    if sudoku[x][y] == "" or sudoku[x][y] == 0:   # update points
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


def check_column_range(column_num):
    column_range_begin = None
    column_range_end = None

    if 0 <= column_num <= 2:
        column_range_begin = 0
        column_range_end = 3
    elif 3 <= column_num <= 5:
        column_range_begin = 3
        column_range_end = 6
    elif 6 <= column_num <= 8:
        column_range_begin = 6
        column_range_end = 9
    else:
        print("Incorrect column num")

    return column_range_begin, column_range_end


def get_count(id, history_id, row_arg, column_arg):
    column = [False] * 10
    row = [False] * 10
    box = [False] * 10

    # column and row
    for i in range(9):
        column_num = firebase_ref.getRef().child('history').child(str(history_id)).child(str(id)).child(
            'numbers').child(str(i)).child(str(column_arg)).get()
        row_num = firebase_ref.getRef().child('history').child(str(history_id)).child(str(id)).child('numbers').child(
            row_arg).child(str(i)).get()
        if column_num != "":
            solved_column_num = firebase_ref.getRef().child('solved_sudoku').child(str(id)).child('numbers').child(
                str(i)).child(column_arg).get()
            if (column_num != 0 and int(column_num) == solved_column_num) or column_num == 0:
                column[solved_column_num] = True

        if row_num != "":
            solved_row_num = firebase_ref.getRef().child('solved_sudoku').child(str(id)).child('numbers').child(
                row_arg).child(str(i)).get()
            if (row_num != 0 and int(row_num) == solved_row_num) or row_num == 0:
                row[solved_row_num] = True

    # box
    row_range_begin = None
    column_range_begin = None
    row_range_end = None
    column_range_end = None

    if 0 <= int(row_arg) <= 2:
        row_range_begin = 0
        row_range_end = 3

        column_range_begin, column_range_end = check_column_range(int(column_arg))

    elif 3 <= int(row_arg) <= 5:
        row_range_begin = 3
        row_range_end = 6

        column_range_begin, column_range_end = check_column_range(int(column_arg))

    elif 6 <= int(row_arg) <= 8:
        row_range_begin = 6
        row_range_end = 9

        column_range_begin, column_range_end = check_column_range(int(column_arg))

    for i in range(row_range_begin, row_range_end):
        for j in range(column_range_begin, column_range_end):
            box_num = firebase_ref.getRef().child('history').child(str(history_id)).child(str(id)).child(
                'numbers').child(str(i)).child(str(j)).get()
            if box_num != "":
                solved_box_num = firebase_ref.getRef().child('solved_sudoku').child(str(id)).child(
                    'numbers').child(str(i)).child(str(j)).get()
                if (box_num != 0 and int(box_num) == solved_box_num) or box_num == 0:
                    box[solved_box_num] = True

    res = []
    for i in range(1, 10):
        if row[i] == False and column[i] == False and box[i] == False:
            res.append(i)

    return res


def update_progress_bar(uid, sudoku_id, value):
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(value)


def reset_game(uid, sudoku_id):
    unsolved_sudoku = firebase_ref.getRef().child('unsolved_sudoku').child(str(sudoku_id)).get()
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).set(unsolved_sudoku)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('hints').set("")
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('game_points').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(0)).set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(1)).set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(2)).set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('used_corrections').set(0)
    firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('used_hints').set(0)



from firebase_connection import firebase_ref
from firebase_connection.firebase_ranking import update_ranking


def get_unsolved(id):
    return firebase_ref.get_db_reference().child('unsolved_sudoku').child(str(id)).child("numbers").get()


def get_solved(id):
    return firebase_ref.get_db_reference().child('solved_sudoku').child(str(id)).child("numbers").get()


def get_level(id):
    return firebase_ref.get_db_reference().child('solved_sudoku').child(str(id)).child("level").get()


def get_user_solution(uid, sudoku_id, is_multiplayer):
    if uid is None:
        return

    history = firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id))

    if history.get() is None:  # game needs to be added to user's game history
        data = {
            'numbers': [[0 for _ in range(9)] for _ in range(9)],
            'time': [0, 0, 0],
            'game_points': 0,
            'used_hints': 0,
            'used_corrections': 0,
            'progress_bar': 0.0,
            'hints': "",
            'possible': [[[0] for _ in range(9)] for _ in range(9)]
        }
        history.set(data)
        no_played = firebase_ref.get_db_reference().child('users').child(uid).child('no_played').get()  # update user statistics
        if not is_multiplayer:
            firebase_ref.get_db_reference().child('users').child(uid).child('no_played').set(no_played + 1)

    return history.child('numbers').get()


def update_user_solution(uid, sudoku_id, x, y, val, is_multiplayer):  # insert number to user's game history
    sudoku = get_user_solution(uid, sudoku_id, is_multiplayer)
    if not sudoku[x][y]:   # update points
        points = firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child("game_points")
        points.set(points.get() + 50)
    sudoku[x][y] = val
    return firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child("numbers").set(sudoku)


def get_users_possible(uid, sudoku_id, x, y):
    result = firebase_ref.get_db_reference().child("history").child(uid).child(str(sudoku_id)).child("possible").child(str(x)).child(str(y)).get()
    if result.count(0) > 0:
        result.remove(0)
    return str(result)[1:len(str(result))-1]


def update_users_possible(uid, sudoku_id, x, y, vals):
    v = vals.split(", ")
    firebase_ref.get_db_reference().child("history").child(uid).child(str(sudoku_id)).child("possible").child(str(x)).child(str(y)).set(v)


def finish_game(uid, sudoku_id):  # update user's statistics and total points
    user_data = firebase_ref.get_db_reference().child('users').child(str(uid))
    game_data = firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id))

    no_won = user_data.child('no_won')
    no_won.set(no_won.get() + 1)

    total_points = user_data.child('total_points').get()
    time = game_data.child("time").get()
    seconds = time[0] * 3600 + time[1] * 60 + time[2]
    game_points = game_data.child('game_points').get()
    gained = game_points * get_level(sudoku_id) * 10 / seconds
    used = game_data.child("used_corrections").get() * 10 + game_data.child("used_hints").get() * 15
    user_data.child('total_points').set(round(total_points + gained - used))

    update_ranking(uid)


def get_all_solved_sudoku():
    return firebase_ref.get_db_reference().child('solved_sudoku').get()


def get_sudoku_with_level(level):
    all_sudoku = get_all_solved_sudoku()
    lvl_sudoku = []
    for i in range(len(all_sudoku)):
        if all_sudoku[i]['level'] == level:
            lvl_sudoku.append(all_sudoku[i]['id'])
    return lvl_sudoku


def get_hint(id, history_id, square, field):
    print(square, field)
    num = firebase_ref.get_db_reference().child('solved_sudoku').child(str(id)).child('numbers').child(square).child(field).get()
    firebase_ref.get_db_reference().child('history').child(str(history_id)).child(str(id)).child('numbers').child(square).child(field).set(num)
    return num


def get_count(id, history_id, row_arg, column_arg):
    is_taken = [False for _ in range(9)]
    users_numbers = firebase_ref.get_db_reference().child('history').child(str(history_id)).child(str(id)).child('numbers')
    correct_numbers = firebase_ref.get_db_reference().child('solved_sudoku').child(str(id)).child('numbers')

    # column and row
    for i in range(9):
        column_num = users_numbers.child(str(i)).child(str(column_arg)).get()
        row_num = users_numbers.child(row_arg).child(str(i)).get()
        if column_num:
            solved_column_num = correct_numbers.child(str(i)).child(column_arg).get()
            if int(column_num) == solved_column_num:
                is_taken[solved_column_num-1] = True

        if row_num:
            solved_row_num = correct_numbers.child(row_arg).child(str(i)).get()
            if int(row_num) == solved_row_num:
                is_taken[solved_row_num-1] = True

    # box
    row_range_begin = 3 * (int(row_arg) // 3)
    row_range_end = row_range_begin + 3
    column_range_begin = 3 * (int(column_arg) // 3)
    column_range_end = column_range_begin + 3
    for i in range(row_range_begin, row_range_end):
        for j in range(column_range_begin, column_range_end):
            box_num = users_numbers.child(str(i)).child(str(j)).get()
            solved_box_num = correct_numbers.child(str(i)).child(str(j)).get()
            if box_num and int(box_num) == solved_box_num:
                is_taken[solved_box_num-1] = True

    res = [i+1 for i in range(9) if not is_taken[i]]
    return res


def update_progress_bar(uid, sudoku_id, value):
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(value)


def reset_game(uid, sudoku_id):
    unsolved_sudoku = firebase_ref.get_db_reference().child('unsolved_sudoku').child(str(sudoku_id)).get()
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).set(unsolved_sudoku)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('hints').set("")
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('game_points').set(0)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').set(0)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(0)).set(0)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(1)).set(0)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child(str(2)).set(0)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('used_corrections').set(0)
    firebase_ref.get_db_reference().child('history').child(str(uid)).child(str(sudoku_id)).child('used_hints').set(0)



from firebase_connection import firebase_sudoku, firebase_ref


def check_done(uid, sudoku_id, sudoku, is_multiplayer):
    user_sudoku = firebase_sudoku.get_user_solution(uid, sudoku_id, is_multiplayer)
    end = True
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0 and not user_sudoku[i][j]:  # there are still empty fields
                end = False
                break
        if not end:
            break
    if end and len(get_errors_calc(user_sudoku, firebase_sudoku.get_unsolved(sudoku_id))) == 0:
        firebase_sudoku.finish_game(uid, sudoku_id)


def get_errors_db(sudoku_id, sudoku):
    errors = []
    correct_sudoku = firebase_ref.get_db_reference().child("solved_sudoku").child(str(sudoku_id)).child("numbers").get()
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] and str(sudoku[i][j]) != str(correct_sudoku[i][j]):
                errors.append((i, j))
    return errors


def get_errors_calc(user_sudoku, original_sudoku):
    return merge(check_rows(user_sudoku, original_sudoku),
                 check_cols(user_sudoku, original_sudoku),
                 check_squares(user_sudoku, original_sudoku))


def merge(a, b, c):
    for i in range(len(b)):
        if a.count(b[i]) == 0:
            a.append(b[i])

    for i in range(len(c)):
        if a.count(c[i]) == 0:
            a.append(c[i])
    return a


def check_rows(users_sudoku, original_sudoku):
    errors = []
    for i in range(9):
        row = [users_sudoku[i][j] if users_sudoku[i][j] else original_sudoku[i][j] for j in range(9)]
        for j in range(1, 10):
            if row.count(j) + row.count(str(j)) > 1:  # there are repeated numbers in the row
                occurrences = [ind for ind, num in enumerate(row) if num == str(j)]
                for col_num in occurrences:
                    errors.append((i, col_num))
    return errors


def check_cols(users_sudoku, original_sudoku):
    errors = []
    for i in range(9):
        col = [users_sudoku[j][i] if users_sudoku[j][i] else original_sudoku[j][i] for j in range(9)]
        for j in range(1, 10):
            if col.count(j) + col.count(str(j)) > 1:
                occurrences = [ind for ind, num in enumerate(col) if num == str(j)]
                for col_num in occurrences:
                    errors.append((col_num, i))
    return errors


def check_squares(users_sudoku, original_sudoku):
    errors = []
    for i in range(3):
        for j in range(3):
            square = [0 for _ in range(9)]
            ind = 0
            for row in range(3*i, 3*i+3):
                for col in range(3*j, 3*j+3):
                    square[ind] = users_sudoku[row][col] if users_sudoku[row][col] else original_sudoku[row][col]
                    ind += 1
            for k in range(1, 10):
                if square.count(k) + square.count(str(k)) > 1:
                    occurrences = [ind for ind, num in enumerate(square) if num == str(k)]
                    for index in occurrences:
                        errors.append((3 * i + index // 3, 3 * j + index % 3))
    return errors


def find_value_in_map(map, val):
    for k, v in map.items():
        if v == val:
            return k
    return -1

from firebase_connection import firebase_sudoku, firebase_ref


def checkDone(uid, sudoku_id, sudoku):
    user_sudoku = firebase_sudoku.getUserSolution(uid, sudoku_id)
    end = True
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0 and (user_sudoku[i][j] == 0 or user_sudoku[i][j] == ""):
                end = False
    if end and len(getErrorsCalc(sudoku_id, user_sudoku)) == 0:
        firebase_sudoku.finishGame(uid, sudoku_id)


def getErrorsDB(sudoku_id, sudoku):
    errors = []
    correct_sudoku = firebase_ref.getRef().child("solved_sudoku").child(str(sudoku_id)).child("numbers").get()
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] != 0 and sudoku[i][j] != "":
                if str(sudoku[i][j]) != str(correct_sudoku[i][j]):
                    errors.append((i, j))
    return errors


def getErrorsCalc(sudoku):
    all_errors = merge(checkRows(sudoku),
                       checkCols(sudoku),
                       checkSquares(sudoku))
    return all_errors


def merge(a, b, c):
    for i in range(len(b)):
        if a.count(b[i]) == 0:
            a.append(b[i])

    for i in range(len(c)):
        if a.count(c[i]) == 0:
            a.append(c[i])

    return a


def checkRows(users_sudoku):
    errors = []
    for i in range(9):
        row = users_sudoku[i]
        for j in range(1, 10):
            if row.count(j) + row.count(str(j)) > 1:
                for k in range(row.count(str(j))):
                    errors.append((i, row.index(str(j))))
    return errors


def checkCols(users_sudoku):
    errors = []
    for i in range(9):
        col = [0 for _ in range(9)]
        for j in range(9):
            col[j] = users_sudoku[j][i]
        for j in range(1, 10):
            if col.count(j) + col.count(str(j)) > 1:
                for k in range(col.count(str(j))):
                    errors.append((col.index(str(j)), i))
    return errors


def checkSquares(users_sudoku):
    errors = []
    for i in range(3):
        for j in range(3):
            square = [0 for _ in range(9)]
            ind = 0
            for row in range(3*i, 3*i+3):
                for col in range(3*j, 3*j+3):
                    square[ind] = users_sudoku[row][col]
                    ind += 1
            for k in range(1, 10):
                if square.count(k) + square.count(str(k)) > 1:
                    for m in range(square.count(str(k))):
                        ind = square.index(str(k))
                        errors.append((3*i + ind // 3, 3*i + ind % 3))
    return errors


def findValInMap(map, val):
    for k, v in map.items():
        if v == val:
            return k
    return -1


import datetime
import kivy
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import re
from firebase_connection import firebase_sudoku
from firebase_connection import firebase_auth

kivy.require('2.1.0')
kv = Builder.load_file('./board.kv')


sudoku_id = 0  # to be done
sudoku = firebase_sudoku.getUnsolved(sudoku_id)
user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id)
input_map = {}  # map of NumberInput objects created in order to update firebase


def checkDone():
    global user_sudoku
    user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id)
    end = True
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0 and (user_sudoku[i][j] == 0 or sudoku[i][j] == ""):
                end = False
    if end:
        firebase_sudoku.finishGame(firebase_auth.getUID(), sudoku_id)


def checkChanges(instance, value):
    global user_sudoku
    user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id)

    for (i, j) in input_map.keys():
        num = input_map.get((i, j))
        if str(user_sudoku[i][j]) != num.text:
            firebase_sudoku.updateUserSolution(firebase_auth.getUID(), sudoku_id, i, j, num.text)

    checkDone()


class NumberLabel(Label):  # custom label for displaying numbers in sudoku
    pass


class NumberInput(TextInput):   # custom text input to verify user input (only one digit)
    def insert_text(self, substring, from_undo=False):
        self.text = ''
        pat = re.sub('[^1-9]$', '', substring)
        return super().insert_text(pat, from_undo=from_undo)


class BoardSmall(GridLayout):  # small square 3x3
    def create(self, row, col):
        for i in range(3*row, 3*row+3):
            for j in range(3*col, 3*col+3):
                if sudoku[i][j] == 0:
                    n_input = NumberInput()
                    if user_sudoku[i][j] != 0:
                        n_input = NumberInput(text=str(user_sudoku[i][j]))

                    input_map[(i, j)] = n_input
                    self.add_widget(n_input)
                    n_input.bind(text=checkChanges)

                else:
                    self.add_widget(NumberLabel(text=str(sudoku[i][j]), color=(0, 0, 0)))
        return self


class BoardSudoku(GridLayout):  # whole sudoku board, made of 9 BoardSmall
    def create(self):
        for i in range(3):
            for j in range(3):
                box = BoardSmall().create(i, j)
                self.add_widget(box)
        return self


class GameWindow(Screen):
    def build(self):
        global user_sudoku
        uid = firebase_auth.getUID()
        user_sudoku = firebase_sudoku.getUserSolution(uid, sudoku_id)
        board = self.ids.sudoku
        s = BoardSudoku().create()
        board.add_widget(s)

        self.modes = (
            '%I:%m:%S',
            '%H:%m:%S %P',
            '%S:',
        )
        self.mode = 0
        Clock.schedule_interval(self.update_label, 0.01)

    def update_label(self, dt):
        # self.ids.counter.text = str(float(self.ids.counter.text) - 0.01)
        now = datetime.datetime.now()
        self.ids.counter.text = now.strftime(self.modes[self.mode])
        if self.mode == 2:
            self.ids.counter.text += str(now.microsecond)[:3]


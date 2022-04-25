import datetime
import kivy
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import re

import firebase_connection.firebase_ref
from firebase_connection import firebase_sudoku
from firebase_connection import firebase_auth
from frontend import levels

from kivy.uix.popup import Popup


kivy.require('2.1.0')
kv = Builder.load_file('./board.kv')


sudoku_id = 0
sudoku = firebase_sudoku.getUnsolved(sudoku_id)
user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id)
input_map = {}  # map of NumberInput objects created in order to update firebase

progress_bar = None

def checkDone():
    global user_sudoku
    user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id)
    end = True
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0 and (user_sudoku[i][j] == 0 or user_sudoku[i][j] == ""):
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
            if num.text != "":
                ProgressBar.add(progress_bar)
                firebase_sudoku.update_progress_bar(firebase_auth.getUID(), sudoku_id, ProgressBar.get_currect_value(progress_bar))
            else:
                ProgressBar.subtract(progress_bar)
                firebase_sudoku.update_progress_bar(firebase_auth.getUID(), sudoku_id, ProgressBar.get_currect_value(progress_bar))


    checkDone()

class PopUpButtons(FloatLayout):
    # function that displays the content
    def popGet(self):
        show = PopUpButtons()
        window = Popup(title="popup", content=show, size_hint=(None, None), size=(300, 300))
        window.open()

    row = ObjectProperty(None)
    column = ObjectProperty(None)

    def get_hint(self):
        num = firebase_sudoku.get_hint(sudoku_id, firebase_auth.getUID(), self.row.text, self.column.text)
        #TODO: wyświetlenie w komórce tekstowej cyfry

        # i = int(self.row.text)
        # j = int(self.column.text)
        # n_input = NumberInput(text=str(user_sudoku[i][j]))
        # input_map[(i, j)] = n_input

        # user_sudoku[int(self.row.text)][int(self.column.text)] = num
        # firebase_sudoku.updateUserSolution(firebase_auth.getUID(), sudoku_id, self.row.text, self.column.text, num)


class NumberLabel(Label):  # custom label for displaying numbers in sudoku
    pass


class NumberInput(TextInput):   # custom text input to verify user input (only one digit)
    id = ObjectProperty(None)
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
                    if user_sudoku is not None and user_sudoku[i][j] != 0:
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

class Timer(Label):
    def get_time(self, uid, sudoku_id):
        s = firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child('2').get()
        m = firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child('1').get()
        h = firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child('0').get()

        return h, m, s

class ProgressBar():
    def get_progress_bar(self, uid, sudoku_id):
        return firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('progress_bar').get()
    def add(self):
        self.value = self.value + .25

    def subtract(self):
        self.value = self.value - .25

    def get_currect_value(self):
        return progress_bar.value


class GameWindow(Screen):
    def build(self):
        global sudoku_id, user_sudoku, sudoku
        uid = firebase_auth.getUID()
        user_sudoku = firebase_sudoku.getUserSolution(uid, sudoku_id)
        sudoku_id = levels.selected_sudoku
        user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id)
        sudoku = firebase_sudoku.getUnsolved(sudoku_id)

        board = self.ids.sudoku

        s = BoardSudoku().create()
        board.add_widget(s)

        # Progress bar
        global progress_bar
        progress_bar = self.ids.my_progress_bar
        progress_bar.value = ProgressBar().get_progress_bar(uid, sudoku_id)

        #Timer
        self.ids.counter.second = Timer().get_time(uid, sudoku_id)[2]
        self.ids.counter.minute = Timer().get_time(uid, sudoku_id)[1]
        self.ids.counter.hour = Timer().get_time(uid, sudoku_id)[0]

        Clock.schedule_interval(self.update_label, 1)


    def update_label(self, obj):
        self.ids.counter.second += 1
        if self.ids.counter.second == 60:
            if self.ids.counter.minute + 1 > 59:
                self.ids.counter.minute = 0
                self.ids.counter.second = 0
                self.ids.counter.hour += 1

            else:
                self.ids.counter.minute += 1
                self.ids.counter.second = 0


        h = '0' + str(self.ids.counter.hour) if len(str(self.ids.counter.hour)) == 1 else str(self.ids.counter.hour)
        m = '0' + str(self.ids.counter.minute) if len(str(self.ids.counter.minute)) == 1 else str(self.ids.counter.minute)
        s = '0' + str(self.ids.counter.second) if len(str(self.ids.counter.second)) == 1 else str(self.ids.counter.second)

        self.ids.counter.text = h + ':' + m + ':' + s

    def get_popup(self):
        PopUpButtons.popGet(self)

    def count_hint(self):
        pass

    def press_it(self):
        print("get!")

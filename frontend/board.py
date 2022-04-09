import datetime
import kivy
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import re

kivy.require('2.1.0')
kv = Builder.load_file('./board.kv')


sudoku = [[1, 2, 3, 4, 5, 6, 7, 8, 9],   # example sudoku, needs changing to actual import from firebase
          [1, 2, 0, 4, 5, 6, 7, 8, 9],
          [1, 2, 0, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 0, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 0, 8, 9],
          [1, 2, 0, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9]]


class NumberLabel(Label):  # custom label for displaying numbers in sudoku
    pass


class NumberInput(TextInput):   # custom text input to verify user input (only one digit)
    def insert_text(self, substring, from_undo=False):
        self.text = ''
        pat = re.sub('[^0-9]$', '', substring)
        return super().insert_text(pat, from_undo=from_undo)


class BoardSmall(GridLayout):  # small square 3x3
    def create(self, row, col):
        for i in range(3*row, 3*row+3):
            for j in range(3*col, 3*col+3):
                if sudoku[i][j] == 0:
                    self.add_widget(NumberInput())
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






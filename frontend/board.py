import datetime
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import re

kivy.require('2.1.0')

sudoku = [[1, 2, 3, 4, 5, 6, 7, 8, 9],   # example sudoku, needs changing to actual import from firebase
          [1, 2, 0, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9],
          [1, 2, 3, 4, 5, 6, 7, 8, 9]]


class NumberLabel(Label):  # custom label for displaying numbers in sudoku
    pass


class NumberInput(TextInput):   # custom text input to verify user input (only one digit)
    def insert_text(self, substring, from_undo=False):
        self.text = ''
        pat = re.sub('[^0-9]$', '', substring)
        if len(pat) > 1:
            pat = pat[len(pat)-1]
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


class BoardGrid(GridLayout):
    pass


class BoardApp(App):
    def build(self):
        return BoardGrid()

    def on_start(self):
        board = self.root.ids.sudoku
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
        # self.root.ids.counter.text = str(float(self.root.ids.counter.text) - 0.01)
        now = datetime.datetime.now()
        self.root.ids.counter.text = now.strftime(self.modes[self.mode])
        if self.mode == 2:
            self.root.ids.counter.text += str(now.microsecond)[:3]

    # return sudoku_layout


if __name__ == "__main__":
    BoardApp().run()


import kivy
from kivy.app import App
from kivy.uix.label import Label

from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from kivy.uix.widget import Widget
kivy.require('2.1.0')

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

import datetime

# class boardGrid(GridLayout):
#     def __init__(self, **kwargs):
#         super(boardGrid, self).__init__(**kwargs)
#         self.cols = 2
#         self.add_widget(Label(text="labelka"))
#         self.add_widget(Label(text="labelka"))
#         self.add_widget(Label(text="labelka"))

class BoardSmall(Widget):
    pass

class BoardGrid(Widget):
    pass



class BoardApp(App):
    def build(self):
        return BoardGrid()
        # return Label(text="elo!")

    def on_start(self):
        board = self.root.ids.sudoku
        for i in range(3):
            board_row = BoxLayout(orientation="horizontal")
            for j in range(9):
                if j == 3 or j == 4 or j == 5:
                    board_row.add_widget(TextInput(multiline=False, background_color=[1,1,1,1], height=20, border=[1,10,1,1], cursor=[0.5, 0.5]))
                else:
                    board_row.add_widget(TextInput(multiline=False, background_color=[0,0.94,0.84,1], height=20, border=[1,10,1,1]))
            board.add_widget(board_row)

        for i in range(3):
            board_row = BoxLayout(orientation="horizontal")
            for j in range(9):
                if j == 3 or j == 4 or j == 5:
                    board_row.add_widget(TextInput(multiline=False, background_color=[0,0.94,0.84,1], height=20, border=[1,10,1,1]))
                else:
                    board_row.add_widget(TextInput(multiline=False, background_color=[1,1,1,1], height=20, border=[1,10,1,1]))

            board.add_widget(board_row)

        for i in range(3):
            board_row = BoxLayout(orientation="horizontal")
            for j in range(9):
                if j == 3 or j == 4 or j == 5:
                    board_row.add_widget(TextInput(multiline=False, background_color=[1,1,1,1], height=20, border=[1,10,1,1]))
                else:
                    board_row.add_widget(TextInput(multiline=False, background_color=[0,0.94,0.84,1], height=20, border=[1,10,1,1]))
            board.add_widget(board_row)

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

    # def sudoku_field(self):
    #     sudoku_layout = GridLayout(cols=3, rows=3, spacing=[10, 10], height=70)
    #     for num in range(1, 10):
    #         box_layout = GridLayout(count=num, cols=3, rows=3)
    #         self.buttons[num] = []
    #         for _ in range(9):
    #             cell = TextInput(count=num, multiline=False, halign='center', font_size=40)
    #             self.buttons[num].append(cell)
    #             box_layout.add_widget(cell)
    #         sudoku_layout.add_widget(box_layout)

        # return sudoku_layout

if __name__ == "__main__":
    BoardApp().run()
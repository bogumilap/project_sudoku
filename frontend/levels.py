import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from firebase_connection import firebase_sudoku
from firebase_connection import firebase_ranking
kivy.require('2.1.0')

level = 1
selected_sudoku = 0
is_multiplayer = False
is_clicked = False
#  najpeirw jest levels, potem menu

class levelsWindow(Screen):
    def build(self):
        self.ids.ranking.clear_widgets()

        ranking = firebase_ranking.getRanking()
        for i in range(5):
            pos = ranking[i]
            text = str(i+1) + ". " + pos[0] + "   " + str(pos[1])
            self.ids.ranking.add_widget(Label(text=text, color='111111'))

    def changeLevel(self, lvl):
        global level
        level = lvl
        App.get_running_app().root.current = "menuWindow"

    def multiplayer_game(self):
        global is_multiplayer
        is_multiplayer = not is_multiplayer
        print(is_multiplayer)

    def multiplayer_color(self):
        global is_clicked
        is_clicked = not is_clicked
        if is_clicked:
            self.ids.multiplayer.background_color = [18/255,186/255,149/255,1]
        else:
            self.ids.multiplayer.background_color = [1, 0, 0, 1]


class menuWindow(Screen):
    def build(self):
        menu = firebase_sudoku.getSudokuWithLevel(level)

        grid = GridLayout(rows=7, row_force_default=True, row_default_height=100, cols=7, col_force_default=True,
                          col_default_width=100, spacing=(3,3), pos_hint={"top": 0.87})
        for i in range(len(menu)):
            b = Button(text="sudoku "+str(i+1))
            b.bind(on_release=showSudoku)
            grid.add_widget(b)

        self.add_widget(grid)

    def returning(self):
        App.get_running_app().root.current = "levelsWindow"


def showSudoku(arg):
    global selected_sudoku
    selected_sudoku = firebase_sudoku.getSudokuWithLevel(level)[eval(arg.text[7:])-1]
    App.get_running_app().root.current = "GameWindow"



kv = Builder.load_file('./levels.kv')

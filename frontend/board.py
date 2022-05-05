import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import re

import firebase_connection.firebase_ref
from backend.sudoku_checks import checkDone
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
game_window = None


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
    checkDone(firebase_auth.getUID(), sudoku_id, sudoku)


class DataTable(BoxLayout):
    def __init__(self,table='', **kwargs):
        super().__init__(**kwargs)

        data = firebase_connection.firebase_ref.getRef().child('history').child(str(firebase_auth.getUID()))\
            .child(str(sudoku_id)).child('database')

        column_titles = ["lp", "row", "column", "numbers"]
        self.columns = 4
        rows_length = len(data.get())
        table_data = []
        for y in column_titles:
            table_data.append({'text':str(y),'size_hint_y':None,'height':30,'bcolor':(0,135/255,85/255,1)})

        for i in range(rows_length):
            table_data.append({'text':str(i),'size_hint_y':None,'height':20,'bcolor':(94/255,209/255,121/255,1)})
            table_data.append({'text':str(data.child(str(i)).child('row').get()),'size_hint_y':None,'height':20,'bcolor':(94/255,209/255,121/255,1)})
            table_data.append({'text':str(data.child(str(i)).child('column').get()),'size_hint_y':None,'height':20,'bcolor':(94/255,209/255,121/255,1)})
            table_data.append({'text':str(data.child(str(i)).child('numbers').get()),'size_hint_y':None,'height':20,'bcolor':(94/255,209/255,121/255,1)})

        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data


class PopUpHints(FloatLayout):
    row = ObjectProperty(None)
    column = ObjectProperty(None)

    def popGet(self):
        self.show = PopUpHints()
        btn1 = Button(text="GET", size_hint=(0.6, 0.2), pos_hint={"x": 0.2, "top": 0.3})
        self.show.add_widget(btn1)
        self.window = Popup(title="Get the hint!", content=self.show, size_hint=(None, None), size=(300, 300))
        btn1.bind(on_press=self.get_hint)
        self.window.open()

    def get_hint(self, obj):
        num = firebase_sudoku.get_hint(sudoku_id, firebase_auth.getUID(), self.show.ids.row.text, self.show.ids.column.text)
        game_window.time.update_time(firebase_auth.getUID(), sudoku_id, game_window.ids.counter.hour, game_window.ids.counter.minute,game_window.ids.counter.second)
        game_window.clock.unschedule(game_window.update_label)
        game_window.refresh()
        self.window.dismiss()

    def popCount(self):
        self.show = PopUpHints()
        btnCount = Button(text="SHOW", size_hint=(0.6, 0.2), pos_hint={"x": 0.2, "top": 0.3})
        self.show.add_widget(btnCount)
        self.window = Popup(title="Show all possible number!", content=self.show, size_hint=(None, None), size=(300, 300))
        btnCount.bind(on_press=self.get_count)
        self.window.open()

    def get_count(self, obj):
        res = firebase_sudoku.get_count(sudoku_id, firebase_auth.getUID(), self.show.ids.row.text, self.show.ids.column.text)
        data_size = len(firebase_connection.firebase_ref.getRef().child('history').child(str(firebase_auth.getUID()))\
            .child(str(sudoku_id)).child('database').get())

        database_data = {
            'column': self.show.ids.column.text,
            'numbers': res,
            'row': self.show.ids.row.text,
        }

        firebase_connection.firebase_ref.getRef().child('history').child(str(firebase_auth.getUID())) \
            .child(str(sudoku_id)).child('database').child(str(data_size)).set(database_data)

        game_window.time.update_time(firebase_auth.getUID(), sudoku_id, game_window.ids.counter.hour, game_window.ids.counter.minute,game_window.ids.counter.second)
        game_window.clock.unschedule(game_window.update_label)
        game_window.refresh()
        self.window.dismiss()


class PopUpPause(FloatLayout):

    def popPause(self):
        self.show = PopUpPause()
        self.show.ids.resume.bind(on_press=self.resume_click)
        self.show.ids.reset.bind(on_press=self.reset_click)
        self.show.ids.exit.bind(on_press=self.exit_click)
        self.window = Popup(title="Pause!", content=self.show, size_hint=(None, None), size=(300, 300))
        self.window.open()

    def resume_click(self, obj):
        game_window.start_timer()
        self.window.dismiss()

    def reset_click(self, obj):
        self.window.dismiss()
        game_window.reset_game()

    def exit_click(self, obj):
        self.window.dismiss()
        game_window.exit_game()


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

    def update_time(self, uid, sudoku_id, hour, minute, second):
        firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child('2').set(second)
        firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child('1').set(minute)
        firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child('time').child('0').set(hour)


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

        self.board = self.ids.sudoku

        self.s = BoardSudoku().create()
        self.board.add_widget(self.s)

        # DataTable
        self.dt = DataTable()
        self.ids.table_id.add_widget(self.dt)

        # Progress bar
        global progress_bar
        progress_bar = self.ids.my_progress_bar
        progress_bar.value = ProgressBar().get_progress_bar(uid, sudoku_id)

        self.time = Timer()
        self.start_timer()

        global game_window
        game_window = self

    def start_timer(self):
        self.ids.counter.second = self.time.get_time(firebase_auth.getUID(), sudoku_id)[2]
        self.ids.counter.minute = self.time.get_time(firebase_auth.getUID(), sudoku_id)[1]
        self.ids.counter.hour = self.time.get_time(firebase_auth.getUID(), sudoku_id)[0]

        self.clock = Clock
        self.clock.schedule_interval(self.update_label, 1)

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

    def get_popup(self, t):
        self.popup_elem = PopUpHints()
        self.popup_pause = PopUpPause()
        if t == "get":
            self.popup_elem.popGet()
        elif t == "count":
            self.popup_elem.popCount()
        elif t == "pause":
            self.clock.unschedule(self.update_label)
            self.time.update_time(firebase_auth.getUID(), sudoku_id, self.ids.counter.hour, self.ids.counter.minute, self.ids.counter.second)
            self.popup_pause.popPause()

    def refresh(self):
        self.ids.table_id.remove_widget(self.dt)
        self.board.remove_widget(self.s)
        self.build()

    def reset_game(self):
        firebase_sudoku.reset_game(firebase_auth.getUID(), sudoku_id)
        self.clock.unschedule(self.update_label)
        self.refresh()

    def exit_game(self):
        self.time.update_time(firebase_auth.getUID(), sudoku_id, self.ids.counter.hour, self.ids.counter.minute,self.ids.counter.second)
        self.ids.table_id.remove_widget(self.dt)
        self.board.remove_widget(self.s)
        self.clock.unschedule(self.update_label)
        App.get_running_app().root.current = "levelsWindow"



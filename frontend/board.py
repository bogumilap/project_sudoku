import kivy
from kivy.app import App
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
from kivy.uix.dropdown import DropDown

import firebase_connection.firebase_ref
from backend.sudoku_checks import checkDone, getErrorsDB, getErrorsCalc, findValInMap
from firebase_connection import firebase_sudoku
from firebase_connection import firebase_auth
from firebase_connection.firebase_sudoku import getUserPossible, updateUserPossible
from frontend import levels

from random import randint

from kivy.uix.popup import Popup

kivy.require('2.1.0')
kv = Builder.load_file('./board.kv')

is_multiplayer = True
multiplayer_changes = False

sudoku_id = 0
sudoku = firebase_sudoku.getUnsolved(sudoku_id)
user_sudoku = firebase_sudoku.getUserSolution(firebase_auth.getUID(), sudoku_id, is_multiplayer)
input_map = {}  # map of NumberInput objects created in order to update firebase
displayed_error = (-1, -1)

progress_bar = None
game_window = None



def refresh_handler(arg):
    global multiplayer_changes
    multiplayer_changes = True


def get_history_id() -> str:
    return firebase_auth.getUID() if not is_multiplayer else 'multiplayer'


def checkChanges(instance, value):
    global user_sudoku, input_map
    user_sudoku = firebase_sudoku.getUserSolution(get_history_id(), sudoku_id, is_multiplayer)
    i, j = findValInMap(input_map, instance)
    firebase_sudoku.updateUserSolution(get_history_id(), sudoku_id, i, j, value, is_multiplayer)

    if value != "":
        ProgressBar.add(progress_bar)
        firebase_sudoku.update_progress_bar(get_history_id(), sudoku_id, ProgressBar.get_currect_value(progress_bar))
    else:
        ProgressBar.subtract(progress_bar)
        firebase_sudoku.update_progress_bar(get_history_id(), sudoku_id, ProgressBar.get_currect_value(progress_bar))
    checkDone(get_history_id(), sudoku_id, sudoku, is_multiplayer)


class NumberLabel(Label):  # custom label for displaying numbers in sudoku
    pass


class NumberInput(TextInput):  # custom text input to verify user input (only one digit)
    id = ObjectProperty(None)

    def insert_text(self, substring, from_undo=False):
        self.foreground_color = (0, 0, 0)
        self.text = ''
        pat = re.sub('[^1-9]$', '', substring)
        return super().insert_text(pat, from_undo=from_undo)

    def showPossible(self, value):
        i, j = findValInMap(input_map, self)
        ListPopup().create(i, j)


class ListPopup(FloatLayout):
    i = -1
    j = -1
    text = ""

    def create(self, i, j):
        self.show = ListPopup()
        self.i = i
        self.j = j
        inp = TextInput(text=getUserPossible(get_history_id(), sudoku_id, i, j))
        inp.bind(text=self.save)
        self.window = Popup(title="your possible numbers", content=inp, size_hint=(None, None), size=(300, 300))
        self.window.open()

    def save(self, instance, value):
        updateUserPossible(get_history_id(), sudoku_id, self.i, self.j, value)


class BoardSmall(GridLayout):  # small square 3x3
    def create(self, row, col):
        global displayed_error
        for i in range(3 * row, 3 * row + 3):
            for j in range(3 * col, 3 * col + 3):
                if sudoku[i][j] == 0:
                    n_input = NumberInput(foreground_color=(0, 0, 0))
                    if user_sudoku is not None and user_sudoku[i][j] != 0 and user_sudoku[i][j] != "":
                        if displayed_error == (i, j):
                            n_input = NumberInput(text=str(user_sudoku[i][j]), foreground_color=(1, 0, 0))
                            displayed_error = (-1, -1)
                        else:
                            n_input = NumberInput(text=str(user_sudoku[i][j]), foreground_color=(0, 0, 0))

                    input_map[(i, j)] = n_input
                    n_input.bind(on_double_tap=n_input.showPossible)
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


class DataTable(BoxLayout):
    def __init__(self, table='', **kwargs):
        super().__init__(**kwargs)

        data = firebase_connection.firebase_ref.getRef().child('history').child(str(get_history_id())) \
            .child(str(sudoku_id)).child('hints')

        column_titles = ["lp", "row", "column", "numbers"]
        self.columns = 4
        rows_length = len(data.get()) if data.get() is not None else 0
        table_data = []
        for y in column_titles:
            table_data.append(
                {'text': str(y), 'size_hint_y': None, 'height': 30, 'bcolor': (0, 135 / 255, 85 / 255, 1)})

        for i in range(rows_length):
            table_data.append(
                {'text': str(i), 'size_hint_y': None, 'height': 20, 'bcolor': (94 / 255, 209 / 255, 121 / 255, 1)})
            table_data.append({'text': str(data.child(str(i)).child('row').get()), 'size_hint_y': None, 'height': 20,
                               'bcolor': (94 / 255, 209 / 255, 121 / 255, 1)})
            table_data.append({'text': str(data.child(str(i)).child('column').get()), 'size_hint_y': None, 'height': 20,
                               'bcolor': (94 / 255, 209 / 255, 121 / 255, 1)})
            table_data.append(
                {'text': str(data.child(str(i)).child('numbers').get()), 'size_hint_y': None, 'height': 20,
                 'bcolor': (94 / 255, 209 / 255, 121 / 255, 1)})

        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data


class CustomDropDown(DropDown):
    pass


class PopUpHints(FloatLayout):
    def popGet(self):
        self.show = PopUpHints()

        self.mainbutton_row = Button(text="Row", size_hint=(0.2, 0.1), pos_hint={"x": 0.4, "top": 0.8})
        self.show.add_widget(self.mainbutton_row)
        dropdown_row = CustomDropDown()
        self.mainbutton_row.bind(on_release=dropdown_row.open)
        dropdown_row.bind(on_select=self.select_text_row)

        self.mainbutton_column = Button(text="Column", size_hint=(0.2, 0.1), pos_hint={"x": 0.4, "top": 0.5})
        self.show.add_widget(self.mainbutton_column)
        dropdown_column = CustomDropDown()
        self.mainbutton_column.bind(on_release=dropdown_column.open)
        dropdown_column.bind(on_select=self.select_text_column)

        btn1 = Button(text="GET", size_hint=(0.6, 0.2), pos_hint={"x": 0.2, "top": 0.3})
        self.show.add_widget(btn1)
        self.window = Popup(title="Get the hint!", content=self.show, size_hint=(None, None), size=(300, 300))
        btn1.bind(on_press=self.get_hint)
        self.window.open()

    def get_hint(self, obj):
        num = firebase_sudoku.get_hint(sudoku_id, get_history_id(), self.mainbutton_row.text,
                                       self.mainbutton_column.text)
        game_window.time.update_time(get_history_id(), sudoku_id, game_window.ids.counter.hour,
                                     game_window.ids.counter.minute, game_window.ids.counter.second)
        game_window.clock.unschedule(game_window.update_label)
        game_window.refresh()
        self.window.dismiss()

    def popCount(self):
        self.show = PopUpHints()

        self.mainbutton_row = Button(text="Row", size_hint=(0.2, 0.1), pos_hint={"x": 0.4, "top": 0.8})
        self.show.add_widget(self.mainbutton_row)
        dropdown_row = CustomDropDown()
        self.mainbutton_row.bind(on_release=dropdown_row.open)
        dropdown_row.bind(on_select=self.select_text_row)

        self.mainbutton_column = Button(text="Column", size_hint=(0.2, 0.1), pos_hint={"x": 0.4, "top": 0.5})
        self.show.add_widget(self.mainbutton_column)
        dropdown_column = CustomDropDown()
        self.mainbutton_column.bind(on_release=dropdown_column.open)
        dropdown_column.bind(on_select=self.select_text_column)

        btnCount = Button(text="SHOW", size_hint=(0.6, 0.2), pos_hint={"x": 0.2, "top": 0.3})
        self.show.add_widget(btnCount)
        self.window = Popup(title="Show all possible number!", content=self.show, size_hint=(None, None),
                            size=(300, 300))
        btnCount.bind(on_press=self.get_count)
        self.window.open()

    def get_count(self, obj):
        res = firebase_sudoku.get_count(sudoku_id, get_history_id(), self.mainbutton_row.text,
                                        self.mainbutton_column.text)
        data_size = len(firebase_connection.firebase_ref.getRef().child('history').child(str(get_history_id())) \
                        .child(str(sudoku_id)).child('hints').get())

        hints_data = {
            'column': self.mainbutton_column.text,
            'numbers': res,
            'row': self.mainbutton_row.text
        }

        firebase_connection.firebase_ref.getRef().child('history').child(str(get_history_id())) \
            .child(str(sudoku_id)).child('hints').child(str(data_size)).set(hints_data)

        game_window.time.update_time(get_history_id(), sudoku_id, game_window.ids.counter.hour,
                                     game_window.ids.counter.minute, game_window.ids.counter.second)
        game_window.clock.unschedule(game_window.update_label)
        game_window.refresh()

        self.window.dismiss()

    def select_text_row(self, instance, x):
        self.mainbutton_row.text = x

    def select_text_column(self, instance, x):
        self.mainbutton_column.text = x

    def select_text_row_count(self, instance, x):
        self.mainbutton_count_row.text = x

    def select_text_column_count(self, instance, x):
        self.mainbutton_count_column.text = x


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


class Timer(Label):
    def get_time(self, uid, sudoku_id):
        s = firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'time').child('2').get()
        m = firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'time').child('1').get()
        h = firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'time').child('0').get()
        return h, m, s

    def update_time(self, uid, sudoku_id, hour, minute, second):
        firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'time').child('2').set(second)
        firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'time').child('1').set(minute)
        firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'time').child('0').set(hour)


class ProgressBar():
    def get_progress_bar(self, uid, sudoku_id):
        return firebase_connection.firebase_ref.getRef().child('history').child(str(uid)).child(str(sudoku_id)).child(
            'progress_bar').get()

    def add(self):
        self.value = self.value + .25

    def subtract(self):
        self.value = self.value - .25

    def get_currect_value(self):
        return progress_bar.value


class P(FloatLayout):
    pass


class GameWindow(Screen):
    def build(self):
        global sudoku_id, user_sudoku, sudoku
        uid = get_history_id()
        user_sudoku = firebase_sudoku.getUserSolution(uid, sudoku_id, is_multiplayer)
        sudoku_id = levels.selected_sudoku
        user_sudoku = firebase_sudoku.getUserSolution(get_history_id(), sudoku_id, is_multiplayer)
        sudoku = firebase_sudoku.getUnsolved(sudoku_id)

        self.board = self.ids.sudoku

        self.s = BoardSudoku().create()
        self.board.add_widget(self.s)

        # DataTable
        self.dt = DataTable()
        self.ids.table_id.add_widget(self.dt)

        data_size = len(firebase_connection.firebase_ref.getRef().child('history').child(str(get_history_id())) \
                        .child(str(sudoku_id)).child('hints').get())
        self.ids.hints.clear_widgets()
        self.ids.hints.add_widget(Label(text="hints left: " + str(max(0, 3-data_size)) + "/3"))

        # Progress bar
        global progress_bar
        progress_bar = self.ids.my_progress_bar
        progress_bar.value = ProgressBar().get_progress_bar(uid, sudoku_id)

        self.time = Timer()
        self.start_timer()
        if is_multiplayer:
            firebase_connection.firebase_ref.getRef().child('history').child('multiplayer').listen(refresh_handler)
            self.ids.pause.disabled = True

        global game_window
        game_window = self

    def start_timer(self):
        self.ids.counter.second = self.time.get_time(get_history_id(), sudoku_id)[2]
        self.ids.counter.minute = self.time.get_time(get_history_id(), sudoku_id)[1]
        self.ids.counter.hour = self.time.get_time(get_history_id(), sudoku_id)[0]

        self.clock = Clock
        self.clock.schedule_interval(self.update_label, 1)

    def check_changes(self, obj):
        global multiplayer_changes
        if multiplayer_changes:
            self.show_changes()
            multiplayer_changes = False

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
        m = '0' + str(self.ids.counter.minute) if len(str(self.ids.counter.minute)) == 1 else str(
            self.ids.counter.minute)
        s = '0' + str(self.ids.counter.second) if len(str(self.ids.counter.second)) == 1 else str(
            self.ids.counter.second)

        self.ids.counter.text = h + ':' + m + ':' + s
        if s[1] == '0':
            self.check_changes("")

    def get_popup(self, t):
        self.popup_elem = PopUpHints()
        self.popup_pause = PopUpPause()
        if t == "get":
            self.popup_elem.popGet()
        elif t == "count":
            self.popup_elem.popCount()
        elif t == "pause":
            self.clock.unschedule(self.update_label)
            self.time.update_time(get_history_id(), sudoku_id, self.ids.counter.hour, self.ids.counter.minute,
                                  self.ids.counter.second)
            self.popup_pause.popPause()

    def show_changes(self):
        self.time.update_time(get_history_id(), sudoku_id, self.ids.counter.hour, self.ids.counter.minute,
                              self.ids.counter.second)
        self.clock.unschedule(self.update_label)
        self.refresh()

    def refresh(self):
        self.ids.table_id.remove_widget(self.dt)
        self.board.remove_widget(self.s)
        data_size = len(firebase_connection.firebase_ref.getRef().child('history').child(str(get_history_id())) \
                        .child(str(sudoku_id)).child('hints').get())
        self.ids.hints.clear_widgets()
        self.ids.hints.add_widget(Label(text="hints left: " + str(max(0, 3-data_size)) + "/3"))
        self.build()

    def reset_game(self):
        firebase_sudoku.reset_game(get_history_id(), sudoku_id)
        self.clock.unschedule(self.update_label)
        self.refresh()

    def exit_game(self):
        self.time.update_time(get_history_id(), sudoku_id, self.ids.counter.hour, self.ids.counter.minute,
                              self.ids.counter.second)
        self.ids.table_id.remove_widget(self.dt)
        self.board.remove_widget(self.s)
        self.clock.unschedule(self.update_label)
        App.get_running_app().root.current = "levelsWindow"

    def displayErrorsDB(self):
        global displayed_error
        errors = getErrorsDB(sudoku_id, firebase_sudoku.getUserSolution(get_history_id(), sudoku_id, is_multiplayer))
        ind = 0
        if len(errors) > 1:
            ind = randint(0, len(errors) - 1)
        displayed_error = errors[ind]
        self.board.remove_widget(self.s)
        self.s = BoardSudoku().create()
        self.board.add_widget(self.s)

    def displayErrorsCalc(self):
        global displayed_error
        errors = getErrorsCalc(firebase_sudoku.getUserSolution(get_history_id(), sudoku_id, is_multiplayer))
        ind = 0
        if len(errors) > 1:
            ind = randint(0, len(errors) - 1)
        displayed_error = errors[ind]
        self.board.remove_widget(self.s)
        self.s = BoardSudoku().create()
        self.board.add_widget(self.s)

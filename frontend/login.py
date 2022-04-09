from firebase_connection import firebase_auth
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
import kivy
kivy.require('2.1.0')

import frontend
from frontend import levels
from frontend import board


# class to call the popup function
class PopupWindow(Widget):
    def btn(self):
        popFun()


# class to build GUI for a popup window
class P(FloatLayout):
    pass


# function that displays the content
def popFun():
    show = P()
    window = Popup(title="popup", content=show, size_hint=(None, None), size=(300, 300))
    window.open()


# class to accept user info and validate it
class loginWindow(Screen):
    email1 = ObjectProperty(None)
    pwd1 = ObjectProperty(None)

    def validate(self):
        result = firebase_auth.login(self.email1.text, self.pwd1.text)
        if result == -1:
            popFun()
        else:
            App.get_running_app().root.current = "levelsWindow"
            self.email1.text = ""
            self.pwd1.text = ""

    # signing up
    nick = ObjectProperty(None)
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)

    def signupbtn(self):
        result = firebase_auth.signup(self.nick.text, self.email.text, self.pwd.text)
        if result != -1:
            App.get_running_app().root.current = "levelsWindow"
            self.nick.text = ""
            self.email.text = ""
            self.pwd.text = ""
        else:
            popFun()


# class for managing screens
class windowManager(ScreenManager):
    pass


# kv file
kv = Builder.load_file('login.kv')
sm = windowManager()

# adding screens

sm.add_widget(loginWindow(name='login'))
sm.add_widget(levels.levelsWindow(name='levelsWindow'))
sm.add_widget(board.GameWindow(name='GameWindow'))


class loginMain(App):
    def build(self):
        return sm


if __name__ == "__main__":
    loginMain().run()

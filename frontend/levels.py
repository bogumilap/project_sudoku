import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

kivy.require('2.1.0')

class levelsWindow(Screen):
    pass


kv = Builder.load_file('./levels.kv')


# def __init__(self, **kwargs):
#     super().__init__(**kwargs)



import random
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.button import Button

class MainLabel(Label):
    def __init__(self, **kwargs):
        super(MainLabel,self).__init__(**kwargs)

class MainButton(Button):
    def __init__(self, **kwargs):
        super(MainButton,self).__init__(**kwargs)



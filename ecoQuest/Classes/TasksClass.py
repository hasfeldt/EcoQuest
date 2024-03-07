import random
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.button import Button

class Task:
    def __init__(self, name, xp_reward, difficulty,):
        self.name = name
        self.xp_reward = xp_reward
        self.difficulty = difficulty
        self.container = ObjectProperty(None) 
class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_random_task(self):
        return random.choice(self.tasks) 

class TaskLabel(Label):
    def __init__(self, **kwargs):
        super(TaskLabel,self).__init__(**kwargs)

class TaskButton(Button):
    def __init__(self, **kwargs):
        super(TaskButton,self).__init__(**kwargs)



                 

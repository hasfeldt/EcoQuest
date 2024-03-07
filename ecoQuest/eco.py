import random
from datetime import date
from Classes.TasksClass import Task, TaskManager, TaskLabel, TaskButton
from Classes.MainClass import MainLabel, MainButton
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics.context_instructions import Color 
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.core.window import Window
class PlayerLayout(GridLayout):
    def __init__(self, **kwargs):
        super(PlayerLayout,self).__init__(**kwargs)


class SetupWidget(Widget):
    pass

class SetupWindow(Screen):

    setup = ObjectProperty(None)
    main_window = ObjectProperty(None)
    def press(self):
        name = self.setup.user_name.text
        player_controller = app.root.player_controller
        player_controller.create_player(name)
        app.root.current_player = player_controller.current_player
        app.root.main_window.player_appearance.set_player_property(app.root.current_player.current_color)

class MainWindow(Screen):
    def update_main_property(self):
        self.player = app.root.current_player
        self.player_name.text = self.player.name
        self.player_lvl.text = "Level: " + str(self.player.lvl)
        self.player_xp.text = "XP: " + str(self.player.xp)
    def on_start_button_press(self):
        if self.player.can_display_tasks():
            app.root.task_window.display_tasks()
            self.player.set_last_task_displayed()
        else:
            print("You have already displayed tasks today.")


class TaskPanel(GridLayout):
    def __init__(self, task, **kwargs):
        super(TaskPanel, self).__init__(**kwargs)
        self.task = task
        self.task.container = self
        self.id = task.id
        self.task_label = TaskLabel(text=task.name)
        self.task_button = TaskButton(text= "View Task")
        self.task_label.background_color = (1, 0, 0, 1)
        self.task_button.background_color = (1, 0, 0, 1)
        self.task_button.bind(on_press=self.open_selected_task)
        self.add_widget(self.task_label)
        self.add_widget(self.task_button)

    def open_selected_task(self, instance):
        self.task_button.text = "changed"
        app.root.selected_task_window.set_task_property(self.task)
        app.root.current = "selected_window"

    def remove_self(self):
        self.parent.remove_widget(self)


class TaskWindow(Screen):
    current_tasks = []

    def display_tasks(self):
        task_layout = self.ids.task_layout
        task_layout.clear_widgets()  # Clear previous tasks
        # Display tasks
        self.completed_tasks = []
        self.current_tasks = []
        for i in range(3):  # Display three tasks

            task = app.root.player_controller.task_manager.get_random_task()
            while task in self.current_tasks:
                task = app.root.player_controller.task_manager.get_random_task()
            self.current_tasks.append(task)
            task.id = len(self.current_tasks) - 1
            task_panel = TaskPanel(task)
            task_layout.add_widget(task_panel)

    def add_task_panel(self):
        task_layout = self.ids.task_layout
        task_manager = app.root.player_controller.task_manager
        available_tasks = [
            task
            for task in task_manager.tasks
            if task not in self.current_tasks and task not in self.completed_tasks
        ]

        if available_tasks:
            task = random.choice(available_tasks)
            self.current_tasks.append(task)
            task.id = len(self.current_tasks) - 1
            task_panel = TaskPanel(task)
            task.container = task_panel
            task_layout.add_widget(task_panel)
        else:
            print("No available tasks to add")

        # self.display_tasks()  # Refresh task list after completing task




class SelectedTaskWindow(Screen):
    def set_task_property(self, task):
        self.task = task
        self.task_label.text = task.name
        self.difficulty_label.text = task.difficulty
        self.xp_label.text = str(task.xp_reward)

    def complete_task(self):
        current_player = app.root.current_player
        if current_player:
            current_player.xp += self.task.xp_reward
            current_player.check_level()
            print(app.root.player_controller.saved_profiles.get(current_player.name).xp)
            print(
                f"{current_player.name} completed task: {self.task.name} (+{self.task.xp_reward} XP) current xp: {current_player.xp} current level: {current_player.lvl} next level : {current_player.next_lvl}"
            )
            
            app.root.current = "task_window"
            self.task.container.remove_self()            
            app.root.task_window.completed_tasks.append(self.task)
            app.root.main_window.update_main_property() 
        else:
            print("No current player selected")

    def skip_task(self):
        task_layout = app.root.task_window.task_layout
        task_layout.remove_widget(self.task.container)
        app.root.task_window.add_task_panel()
        app.root.current = "task_window"

    def back_to_task(self):
        app.root.current = "task_window"


class MainWidget(Widget):
    var_layout = ObjectProperty(None)


class Player:
    def __init__(self, name):
        self.name = name
        self.lvl = 1
        self.xp = 0
        self.next_lvl = 25
        self.lvl_reward = 3
        self.unlocked_colors = {'default': (1, 1 ,1), 'yellow': (1,1,0)}
        self.current_color = self.unlocked_colors.get('default')
        self.last_task_displayed = None
    def check_level(self):
        if self.xp >= self.next_lvl:
            self.lvl += 1
            self.xp -= self.next_lvl
            self.next_lvl = round(self.next_lvl * 1.5)
            self.reward_text = ""
            self.level_reward()
            popup = Popup(title='Level Up', size_hint=(None, None), size=(400, 400))
            layout = GridLayout(rows = 2)
            content=Label( text="You leveled up! You are now level " + str(self.lvl) + self.reward_text )

            button = Button(text='Close')
            button.bind(on_press = popup.dismiss)
            layout.add_widget(content)
            layout.add_widget(button)
            popup.content = layout

            popup.open()
            print(self.lvl)
    
    def level_reward(self):
        rewards = {3: app.root.player_customize_screen.red, 6: app.root.player_customize_screen.cyan}
        if self.lvl >= self.lvl_reward:
            if self.lvl_reward in rewards:
                bg_color = rewards.get(self.lvl_reward).bg_value
                self.unlocked_colors[rewards.get(self.lvl_reward).color_name] = bg_color
                rewards.get(self.lvl_reward).text = (rewards.get(self.lvl_reward).color_name[0].upper() + rewards.get(self.lvl_reward).color_name[1:]) + ""
                self.reward_text = "\n\nYou unlocked a new color! Check your \nCustomize Setting." 
                print(self.unlocked_colors)
            self.lvl_reward = round(self.lvl_reward * 2)  
    def can_display_tasks(self):
        # Check if tasks can be displayed today
        return self.last_task_displayed != date.today() 
    def set_last_task_displayed(self):
        # Set the last task displayed to today's date
        self.last_task_displayed = date.today()

class PlayerAppearance(Widget):
    def __init__(self, **kwargs):
        super(PlayerAppearance, self).__init__(**kwargs)
        self.selected_color = "default"
        self.color = (1,1,1) 
        with self.canvas:

            self.color_instruction = Color(*self.color, mode ="rgb")  
            self.head = Rectangle(pos=(self.center_x, self.top - 50), size=(100, 100))
            # Upper body
            self.upper_body = Rectangle(pos=(self.center_x , self.top - 125), size=(20, 20))
            # Lower body
            self.lower_body = Rectangle(pos=(self.center_x, self.top - 175), size=(20, 20))

        self.bind(size=self.update_rect)
    def update_rect(self, instance, value):
        # Update the positions of body parts when the widget ize changes
        Color(*self.color, mode ="rgb")  
        self.head.pos = (self.center_x - 52.5, self.top - 100)
        self.upper_body.pos = (self.center_x - 14.5, self.top - 120)
        self.lower_body.pos = (self.center_x - 14.5, self.top - 140)
    def set_player_property(self, color):
        if color in app.root.current_player.unlocked_colors:
            app.root.current_player.current_color = app.root.current_player.unlocked_colors.get(color)
        else:
            print('Not unlocked yet ')
        print(app.root.current_player.current_color)
        self.color = app.root.current_player.current_color
        self.color_instruction.rgba = (*self.color, 1) 
      



class PlayerCustomizeScreen(Screen):
    player_appearance = ObjectProperty(None)

    def set_window_position(self):

        self.player_appearance.color_instruction = Color((1,1,1), mode ="rgb")  



            # Upper body
        # Lower body
class PlayerController:
    def __init__(self):
        self.saved_profiles = {}
        self.task_manager = TaskManager()

    def create_player(self, name):
        if name == "":
            print("Try again")
        else:
            player = Player(name)
            self.saved_profiles[name] = player
            self.current_player = player
            print("Successfully Created Player", name, self.current_player)

    def get_current_player(self, name):
        self.current_player = self.saved_profiles.get(name)
        return self.saved_profiles.get(name)

    def generate_tasks(self):
        # Sample tasks
        task1 = Task(
            "Clean the bathroom",
            xp_reward=20,
            difficulty="Easy",
        )
        task2 = Task(
            "Complete coding assignment",
            xp_reward=50,
            difficulty="Medium",
        )
        task3 = Task(
            "Go for a run",
            xp_reward=30,
            difficulty="Easy",
        )
        task4 = Task(
            "Read a book for 30 minutes",
            xp_reward=40,
            difficulty="Medium",
        )
        task5 = Task(
            "Cook a healthy meal",
            xp_reward=60,
            difficulty="Hard",
        )
        # Add tasks to task manager
        self.task_manager.add_task(task1)
        self.task_manager.add_task(task2)
        self.task_manager.add_task(task3)
        self.task_manager.add_task(task4)
        self.task_manager.add_task(task5)

    def get_random_task(self):
        return self.task_manager.get_random_task()


class WindowManager(ScreenManager):
    player_controller = PlayerController()
    current_player = ObjectProperty(None)
    pass


kv = Builder.load_file("eco.kv")


class EcoApp(App):
    name = ObjectProperty(None)

    def build(self):
        self.root.player_controller.generate_tasks()
        return kv


if __name__ == "__main__":
    app = EcoApp()
    app.run()

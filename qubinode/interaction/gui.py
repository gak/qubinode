import kivy

kivy.require('1.0.6')  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from interaction.interaction import Interaction


class GraphicalInteraction(Interaction, App):
    def setup(self):
        self.run()

    def build(self):
        return Label(text='Hello world')

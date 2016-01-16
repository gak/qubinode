import kivy

from qubinode.settings import app

kivy.require('1.0.6')  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label

from interaction import Interaction


class GraphicalInteraction(Interaction, App):
    def __init__(self, config):
        Interaction.__init__(self, config=config)
        App.__init__(self)

    def setup(self):
        self.run()

    def build(self):
        self.title = 'qubinode v{}'.format(app.__version__)
        return Label(text='Hello world')

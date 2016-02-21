#!/usr/bin/env python
import os

from .config import Config


class Qubinode:
    def __init__(self):
        self.config = Config()

    def run(self, **kwargs):
        self.config.setup(**kwargs)
        self.config.root_dir = os.path.abspath(os.path.dirname(__file__))
        print(self.config.root_dir)
        ui = self.config.get_interaction()
        ui.run()


def gui():
    Qubinode().run(gui=True)


def console():
    Qubinode().run(gui=False)


if __name__ == '__main__':
    Qubinode().run()

#!/usr/bin/env python
import yaml

from config import Config


class Qubinode:
    def __init__(self):
        self.config = Config()

    def run(self, **kwargs):
        self.config.setup(**kwargs)
        ui = self.config.get_interaction()
        ui.run()


def gui():
    Qubinode().run(gui=True)


def console():
    Qubinode().run(gui=False)


if __name__ == '__main__':
    Qubinode().run()

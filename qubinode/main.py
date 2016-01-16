#!/usr/bin/env python


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


if __name__ == '__main__':
    Qubinode().run()

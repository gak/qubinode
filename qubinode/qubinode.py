from src.config import Config


class Qubinode:
    def __init__(self, gui=False):
        self.config = Config()
        if gui:
            self.config.gui = True

        self.ui = self.config.interaction

    def run(self):
        self.config.setup()
        self.ui.run()


def gui():
    Qubinode(gui=True).run()

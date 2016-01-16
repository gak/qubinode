import sys

from src.config import Config
from src.local_installer import LocalInstaller
from src.settings.bitcoin import RELEASES


class Qubinode:
    def __init__(self):
        self.config = Config()
        self.interaction = self.config.interaction

    def run(self):
        self.config.setup()

        if self.config.list_releases:
            self.list_releases()
            return

        self.ask_release()

        if self.config.spawn_vm:
            self.boot()

        if self.config.local:
            LocalInstaller(self.config).setup()

    def list_releases(self):
        for release, info in RELEASES.items():
            print(' - {}'.format(release))

    def ask_release(self):
        if self.config.release != 'ask':
            pass
        elif self.config.batch:
            self.config.release = 'xt:0.11.0d'
        else:
            self.list_releases()
            self.config.release = raw_input('Which release to install? ')

        if self.config.release not in RELEASES:
            print('Unknown release: {}'.format(self.config.release))
            sys.exit(-1)

    def boot(self):
        '''
        Run the provider class that will start the VM.

        e.g. the "do" provider will instantiate the DigitalOcean class.
        '''
        fun = globals()[self.config.provider['class']]
        fun(self.config).setup()

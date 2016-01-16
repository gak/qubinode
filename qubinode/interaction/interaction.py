class Interaction(object):
    def __init__(self, config):
        self.config = config

    def setup(self):
        raise NotImplementedError()

    def boot(self):
        '''
        Run the provider class that will start the VM.

        e.g. the "do" provider will instantiate the DigitalOcean class.
        '''
        fun = globals()[self.config.provider['class']]
        fun(self.config).setup()

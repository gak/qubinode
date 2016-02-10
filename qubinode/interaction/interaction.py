class Interaction(object):
    def __init__(self, cfg):
        self.cfg = cfg
        print('setting local cfg', self.cfg)

    def setup(self):
        raise NotImplementedError()

    def boot(self):
        '''
        Run the provider class that will start the VM.

        e.g. the "do" provider will instantiate the DigitalOcean class.
        '''
        fun = globals()[self.cfg.provider['class']]
        fun(self.cfg).setup()

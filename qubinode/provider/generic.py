from .provider import Provider


class GenericProvider(Provider):
    def setup(self):
        self.deploy()

    @property
    def ip_address(self):
        return

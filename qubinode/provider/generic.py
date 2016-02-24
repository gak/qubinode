from .provider import Provider


class GenericProvider(Provider):
    def setup(self):
        self.deploy()

    def ip_address(self):
        return self.config.address

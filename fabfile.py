import yaml

from fabric.operations import local


def ci():
    build()
    push()


def test():
    local('ls -la')


def build():
    local('docker-compose build base')
    local('docker-compose build')


def push():
    for distro, version in releases():
        local(' '.join([
            'docker tag -f',
            'qubinode_{distro}_{version}',
            'qubinode/{distro}:{version}',
        ]).format(**locals()))

        local('docker push qubinode/{distro}:{version}'.format(**locals()))


def releases():
    images = yaml.load(open('docker-compose.yml'))
    for image in images:
        if 'base' in image:
            continue
        yield image.split('_', 1)

def binary():
    local('pyinstaller --clean --onefile --console src/qubinode.py')

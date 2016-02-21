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


def generate_quick_test_docker():
    '''
    This creates a base docker image including the bootstrap.sh commands
    so it doesn't have to apt-get/pip/etc, every test.
    '''
    dockerfile = open('docker/test/quick/Dockerfile', 'w')
    dockerfile.write('# This was generated using generate_quick_test_docker\n')
    dockerfile.write('FROM ubuntu:14.04\n')

    for line in open('qubinode/bootstrap.sh'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('set '):
            continue
        if line.startswith('qubinode'):
            continue
        if line.startswith('echo'):
            continue
        dockerfile.write('RUN {}\n'.format(line))

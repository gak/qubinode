import json
import time

import yaml
from fabric.operations import local


def ci():
    build()
    push()


def test():
    local('ls -la')


def test_integration():
    local('docker-compose up -d test_integration')
    time.sleep(2)
    data = local(
            'docker inspect qubinode_test_integration_1',
            capture=True
    ).stdout
    data = json.loads(data)
    ip_address = data[0]['NetworkSettings']['IPAddress']
    local(' '.join([
        'qubinode deploy',
        '--priv-key=docker/test/base/ssh-keys/test',
        '--address={}'.format(ip_address),
        '--release=bc',
    ]))


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
    dockerfile.write('FROM qubinode_test_base\n')

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

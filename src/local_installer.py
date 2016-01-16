import os
import subprocess


class LocalInstaller:
    def __init__(self, config):
        self.config = config

    def setup(self):
        self.swap()
        self.docker_install()
        self.docker_run()

    def shell(self, cmd):
        return subprocess.call(cmd, shell=True)

    def create_file(self, filename, content):
        open(filename, 'w').write(content)

    def swap(self, mb=2048):
        '''
        Creates and activates a swapfile, defaulting to 2GB.

        Also adds it to /etc/fstab
        '''
        if os.path.exists('/swapfile'):
            print('Swapfile already set up...')
            return

        print('Setting up swapfile')
        self.shell('fallocate -l {}M /swapfile'.format(mb))
        self.shell('chmod 600 /swapfile')
        self.shell('mkswap /swapfile')
        self.shell('swapon /swapfile')

        open('/etc/fstab', 'a').write('\n/swapfile none swap defaults 0 0\n')

    def docker_install(self):
        self.shell(
                'apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 '
                '--recv-keys 58118E89F3A912897C070ADBF76221572C52609D'
        )
        self.create_file(
                '/etc/apt/sources.list.d/docker.list',
                'deb https://apt.dockerproject.org/repo ubuntu-trusty main'
        )
        self.shell('apt-get update')
        self.shell('apt-get install -y docker-engine')

    def docker_run_cmd(self):
        cmd = [
            'docker run',
            '--log-driver=json-file',
            '--log-opt="max-size=1m"',
            '--log-opt="max-file=10"',
            '-d',
            '--restart=always',
            '--volume=/var/bitcoin:/root/.bitcoin',
            '--publish=8333:8333',
        ]

        if self.config.prune:
            cmd.append('-e BITCOIN_PRUNE={}'.format(self.config.prune))

        if self.config.bootstrap:
            cmd.append('-e BITCOIN_BOOTSTRAP={}'.format(self.config.bootstrap))

        cmd.append('qubinode/{}'.format(self.config.release))
        return ' '.join(cmd)

    def docker_run(self):
        cmd = self.docker_run_cmd()
        print('Executing {}'.format(cmd))
        self.shell(cmd)

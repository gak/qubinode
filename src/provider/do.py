import functools
import random
import sys
import textwrap
import time
import traceback

import digitalocean as do

from provider.provider import Provider


class DigitalOcean(Provider):
    def setup(self):
        self.prepare_token()
        self.prepare_ssh()
        self.get_regions()
        self.choose_random_region()
        self.create_droplet()
        try:
            self.wait_for_droplet()
            self.wait_for_ssh()
            self.connect()
            self.deploy()
            self.run()
            self.show_connection_instructions()
        except Exception:
            traceback.print_exc()
            print('\n\nThe was an error during the creation process.')
            destroy = raw_input(
                    '\nWould you like to destroy the vm at {}? '.format(
                            self.ip_address,
                    )
            )
            if destroy and destroy.lower()[0] == 'y':
                self.destroy_with_retry()

    def destroy_with_retry(self):
        print('Destroying!')

        attempts = 10
        while attempts:
            attempts -= 1
            try:
                self.instance.destroy()
                print('Done!')
                return
            except do.baseapi.DataReadError:
                traceback.print_exc()
                print('Something went wrong (still booting?)')
                print('Retrying with {} attempts left...'.format(attempts))
                time.sleep(5)

    def prepare_token(self):
        if self.config.do_token:
            self.token = self.config.do_token
        else:
            self.ask_token()

        self.manager = functools.partial(do.Manager, token=self.token)
        self.droplet = functools.partial(do.Droplet, token=self.token)
        self.ssh_do = functools.partial(do.SSHKey, token=self.token)

    def ask_token(self):
        print(textwrap.dedent('''
            We will now:
             - Generate or reuse an SSH key pair in *TODO* some directory.
             - Create a $5/mo, 512MB, 1 CPU instance in a random data center.

            Once started:
             - A SSH key pair will be left in *TODO* some directory which can
               be used for SSHing into the droplet.
             - Your droplet will continue living forever until you stop it.
             - Your DigitalOcean access token will not be saved to disk and
               will be forgotten once the script has ended.

            Press Ctrl-C to abort!
        '''))

        self.token = raw_input('Enter a DigitalOcean access token: ')

    def prepare_ssh(self):
        self.ssh_id = self.ssh_do(name='qubinode', public_key=self.pub_key)
        if not self.ssh_id.load_by_pub_key(self.pub_key):
            print('Putting public key into DO account...')
            self.ssh_id.create()

    def get_regions(self):
        self.regions = self.manager().get_all_regions()

    def choose_random_region(self):
        self.region = random.choice(self.regions).slug

    def create_droplet(self):
        print('Creating droplet: {} {}'.format(
                self.config.do_size,
                self.region,
        ))
        self.instance = self.droplet(
                name='qubinode',
                region=self.region,
                image='ubuntu-14-04-x64',
                size_slug=self.config.do_size,
                ssh_keys=[self.pub_key],
        )
        self.instance.create()

    def wait_for_droplet(self):
        print('\nWaiting for Droplet (few minutes)...')

        # This fetches metadata on the VM, including the the IP address.
        time.sleep(10)
        self.instance.load()
        self.show_connection_instructions()

        while True:
            time.sleep(2)
            sys.stdout.write('.')
            sys.stdout.flush()
            actions = self.instance.get_actions()
            for action in actions:
                action.load()
                if action.status == 'completed':
                    return

    def show_connection_instructions(self):
        print('IP Address is {}'.format(self.ip_address))
        print('You can access the VM via this command:')
        print('\nssh -i {} root@{}\n'.format(
                self.config.priv_key_path, self.ip_address
        ))

    def wait_for_ssh(self):
        print('\nWaiting a bit for for SSH...')
        time.sleep(10)

    @property
    def ip_address(self):
        return self.instance.ip_address

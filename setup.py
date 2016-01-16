from setuptools import setup, find_packages

setup(
        name="qubinode",
        version="0.0.1",
        packages=['qubinode'],
        entry_points={
            'gui_scripts': [
                'qubinode-gui = qubinode.qubinode.gui',
            ],
            'console_scripts': [
                'qubinode = qubinode.qubinode.console',
            ]
        }
)

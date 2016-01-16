from setuptools import setup

setup(
        name="qubinode",
        version="0.0.1",
        packages=['qubinode'],
        entry_points={
            'gui_scripts': [
                'qubinode-gui = qubinode.main:gui',
            ],
            'console_scripts': [
                'qubinode = qubinode.main:console',
            ]
        }
)

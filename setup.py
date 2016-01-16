from setuptools import setup, find_packages

setup(
        name="qubinode",
        version="0.0.1",
        packages=find_packages(),
        entry_points={
            'qubinode-gui': 'qubinode:gui'
        }
)

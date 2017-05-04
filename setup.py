from distutils.core import setup

from setuptools import find_packages

setup(
    name='mathcp',
    version='0.1',
    url='https://github.com/avladev/mathcp',
    author='Anatoli Vladev',
    author_email='',
    description='TCP math expression solver',
    packages=find_packages(exclude=[]),
    entry_points={
        'console_scripts': [
            'mathcp = mathcp.__main__:main'
        ]
    },
)

import os
from setuptools import setup, find_packages


here = os.path.dirname(os.path.abspath(__file__))


setup(
    name='ntl',
    version='0.0.1',
    packages=find_packages(here),
    url='',
    license='',
    author='',
    author_email='',
    description='',
    install_requires=(
        'jupyter',
        'pandas',
        'matplotlib',
        'numpy'
    )
)

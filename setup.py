from os import path
from io import open
from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="errbot-backend-matrix-nio",
    version="0.5.0",
    url="https://github.com/clouetb/errbot-backend-matrix-nio",
    author='Benoît Clouet',
    author_email="benoit.clouet@gmail.com",
    description=("A simple Errbot backend for matrix.org"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="EUPLv2",
    packages=find_packages(),
    install_requires=[
        "matrix-nio",
        "errbot"
    ],
    extras_require={
        "e2e":  [
            "python-olm>=3.1.0",
            "peewee>=3.9.5",
            "cachetools",
            "atomicwrites",
        ]
    },
    zip_safe=False
)
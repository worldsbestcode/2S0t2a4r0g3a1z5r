#!/usr/bin/env python3

import os
import sys
from setuptools import setup, find_packages

def get_info(name):
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, '__init__.py')) as f:
        locals = {}
        try:
            exec(f.read(), locals)
        except ImportError:
            pass
        try:
            return locals[name]
        except:
            pass
        return None

def get_requirements():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'requirements.txt')) as f:
        locals = []
        try:
            locals = f.readlines()
        except ImportError:
            pass
        return locals

setup(
    name="fxweb",
    keywords=["fxweb"],
    version=get_info('__version__'),
    author=get_info('__author__'),
    author_email=get_info('__email__'),
    maintainer=get_info('__author__'),
    maintainer_email=get_info('__email__'),
    description=get_info('__doc__'),
    license=get_info('__license__'),
    long_description=get_info('__doc__'),
    packages=find_packages(),
    url='https://www.futurex.com',
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'run = run:main',
        ],
    },
)

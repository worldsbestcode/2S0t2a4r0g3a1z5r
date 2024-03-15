#!/usr/bin/env python3

import os
import sys
from setuptools import setup, find_packages

# Pop web project name from args
project = None
for arg in sys.argv:
    if arg.startswith("--project="):
        project = arg[len("--project="):]
        sys.argv.remove(arg)
        break

def get_info(name):
    basedir = os.path.dirname(__file__)
    basedir = os.path.join(basedir, project)
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
    ret = []
    basedir = os.path.dirname(__file__)
    projdir = os.path.join(basedir, project)
    with open(os.path.join(projdir, 'requirements.txt')) as f:
        locals = []
        try:
            locals = f.readlines()
        except ImportError:
            pass
        ret += locals

    shareddir = os.path.join(basedir, "shared")
    with open(os.path.join(shareddir, 'requirements.txt')) as f:
        shared = []
        try:
            shared = f.readlines()
        except ImportError:
            pass
        ret += shared
    return ret

setup(
    name=project + "-web",
    keywords=[project],
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

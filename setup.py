#!/usr/bin/env python
import os
from setuptools import setup

setup(
    # GETTING-STARTED: set your app name:
    name='MyBlog',
    # GETTING-STARTED: set your app version:
    version='1.0',
    # GETTING-STARTED: set your app description:
    description='OpenShift App',
    # GETTING-STARTED: set author name (your name):
    author='Adam Cottrill',
    # GETTING-STARTED: set author email (your email):
    author_email='racottrill@gmail.com',
    # GETTING-STARTED: set author url (your url):
    url='http://www.python.org/sigs/distutils-sig/',
    # GETTING-STARTED: define required django version:
    install_requires =open('%swsgi/requirements/base.txt'
                            % os.environ.get('OPENSHIFT_REPO_DIR')).readlines(),
#    dependency_links=[
#        'https://pypi.python.org/simple/django/'
#    ],
)

#!/usr/bin/env python

from setuptools import setup

setup(
    name='amicleanup',
    version='0.0.1',
    author='Shawn Siefkas',
    author_email='shawn.siefkas@meredith.com',
    description='AMI Cleanup',
    install_requires=[
        'boto3',
    ],
    test_suite = 'test',
    py_modules = ['amicleanup']
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# coding=utf-8
"""
PicDB: image management tool.

Copyright 2016-2018, Stefan Braun.
Licensed under MIT.
"""
import sys
from setuptools import setup

VERSION = '1.1.11'

setup(
    name='picdb',
    version=VERSION,
    packages=['picdb'],
    url='https://github.com/stbraun/picdb',
    license='MIT',
    author='Stefan Braun',
    author_email='sb@action.ms',
    description='Simple image database.',
    include_package_data=True,
    zip_safe=False,
    install_requires=['pillow', 'PyYAML'],
    requires=['pillow', 'PyYAML', 'PyInstaller', 'Sphinx'],
    provides=['picdb'],
    scripts=['scripts/assign_pictures.py', 'start_picdb.py'],
    tests_require=['pytest', 'pytest-cover', 'hypothesis'],
)

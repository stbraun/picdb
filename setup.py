
import sys
from distutils.core import setup

setup(
    name='picdb',
    version='0.1.0dev',
    packages=[''],
    package_dir={'': 'picdb'},
    url='',
    license='BSD',
    author='Stefan Braun',
    author_email='',
    description='Picture Database',
    provides=['picdb'],
    app=["picdb/main.py"]
)

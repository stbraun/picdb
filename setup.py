import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """This is a plug-in for setuptools.

     It will invoke py.test when you run python setup.py test
    """

    def finalize_options(self):
        """Configure."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Execute tests."""
        # import here, because outside the required eggs aren't loaded yet
        import pytest
        sys.exit(pytest.main(self.test_args))


version = '0.1.0.2'

setup(
    name='picdb',
    version=version,
    packages=['picdb'],
    url='',
    license='MIT',
    author='Stefan Braun',
    author_email='sb@action.ms',
    description='Simple image database.',
    include_package_data=True,
    zip_safe=False,
    install_requires=['Pillow', 'PyYAML'],
    requires=['Pillow', 'PyYAML'],
    provides=['picdb'],
    scripts=['scripts/assign_pictures.py', 'start_picdb.py'],
    tests_require=['pytest', 'nose'],
    cmdclass={'test': PyTest},
)

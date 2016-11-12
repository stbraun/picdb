from paver.easy import *
from paver.doctools import html, doc_clean
from paver.setuputils import setup

setup(
    name='picdb',
    version='0.1.1',
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
)

options(
    sphinx=Bunch(
        builddir="build",
        sourcedir="source",
    )
)


@task
def analyze():
    sh("rm reports/flake8.txt")
    sh(
        "flake8 --output-file reports/flake8.txt "
        "--statistics picdb")


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


@task
@needs('install', 'doc_clean', 'html')
def docs_rebuild():
    pass


@task
def uninstall():
    """Uninstall picdb package."""
    sh("pip uninstall picdb")


@task
def build_app():
    sh("echo "'building the system ...'"")
    sh("pyinstaller PicDB.spec")


@task
def clean_app():
    sh("rm -rf dist/PicDB dist/PicDB.app")


@task
def install_app():
    sh("mv dist/PicDB.app /Applications")


@task
@needs('clean', 'sdist', 'install', 'docs_rebuild', 'build_app')
def build():
    pass

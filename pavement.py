""" Provide tasks for build and deployment.

This file provides tasks for paver.
"""

from paver.easy import *
from paver.doctools import html, doc_clean
from paver.setuputils import setup
from picdb.version import long_version


setup(
    name='picdb',
    version=long_version,
    packages=['picdb'],
    url='https://github.com/stbraun/picdb',
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
def clean():
    """Remove build artifacts."""
    sh('rm -rf build dist')


@task
def dependencies():
    """Create a dependency graph.

    Find results in folder reports.
    """
    sh(
        'sfood picdb | tee reports/dependencies.txt | sfood-graph | tee '
        'reports/picdb.gv | dot -Tpdf -o reports/picdb.pdf')


@task
def test_coverage():
    """Run nosetests with coverage."""
    sh('nosetests --with-coverage test/')


@task
def analyze():
    """Analyze project using flake8."""
    sh("rm -f reports/flake8.txt")
    sh(
        "flake8 --output-file reports/flake8.txt --benchmark --count "
        "--statistics picdb start_picdb.py")


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


@task
@needs('install', 'doc_clean', 'html')
def docs():
    """Rebuild documentation."""
    pass


@task
def install():
    """Install package into local environment."""
    sh("pip install .")


@task
def uninstall():
    """Uninstall picdb package."""
    sh("pip uninstall picdb")


@task
def regenerate_spec():
    """Create a new spec for pyinstaller.

    Be aware that you need to modify the created spec to get a working
    configuration.
    """
    sh(
        "pyinstaller --onefile --windowed -n PicDB --additional-hooks-dir "
        "pyinstaller-hooks --runtime-hook "
        "pyinstaller-hooks/pyi_rth__tkinter.py start_picdb.py")


@task
def build_app():
    """Build the app bundle based on an existing spec."""
    sh("echo "'building the system ...'"")
    sh("pyinstaller PicDB.spec")


@task
def clean_app():
    """Remove files generated by pyinstaller."""
    sh("rm -rf dist/PicDB dist/PicDB.app")


@task
@needs('clean', 'test_coverage', 'analyze', 'sdist', 'install', 'build_app',
       'docs')
def build():
    """Perform a complete build."""
    pass


@task
def deploy():
    """Deploy the app bundle on the local machine."""
    sh("cp -Rf dist/PicDB.app /Applications")

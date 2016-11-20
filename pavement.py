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
def dependencies():
    """Create a dependency graph.

    Find results in folder reports.
    """
    sh(
        'sfood picdb | tee reports/dependencies.txt | sfood-graph | tee '
        'reports/picdb.gv | dot -Tpdf -o reports/picdb.pdf')


@task
def testcov():
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
def docs_rebuild():
    pass


@task
def uninstall():
    """Uninstall picdb package."""
    sh("pip uninstall picdb")


@task
def regenerate_spec():
    sh(
        "pyinstaller --onefile --windowed -n PicDB --additional-hooks-dir "
        "pyinstaller-hooks --runtime-hook "
        "pyinstaller-hooks/pyi_rth__tkinter.py start_picdb.py")


@task
def build_app():
    sh("echo "'building the system ...'"")
    sh("pyinstaller PicDB.spec")


@task
def clean_app():
    sh("rm -rf dist/PicDB dist/PicDB.app")


@task
@needs('clean', 'testcov', 'analyze', 'sdist', 'install', 'docs_rebuild',
       'build_app')
def build():
    pass


@task
def deploy():
    sh("mv dist/PicDB.app /Applications")

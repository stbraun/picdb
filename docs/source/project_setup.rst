##########################################
Project Setup and Configuration Management
##########################################


.. toctree::
   :maxdepth: 3


This section describes how to setup the project and how to build and deploy the app.

Tools and Frameworks
********************

The project is developed in *Python 3.5+*. *PyCharm* is used as IDE but not required.

*flake8* is used for static analysis of the source code.

Documentation is created with *Sphinx*.

More tools are mentioned in the following sections.


User interface
==============

The user interface is built using *tkinter* and *ttk*.


Persistence
===========

The image meta-data is stored in a *PostgreSQL* database.
The database is accessed using *py-postgresql*.


Build
*****

*Paver* is used to build the system.
See *pavement.py* for implementation of commands.

Available commands are:

* ``paver dependencies`` - create a dependency graph.
* ``paver test_coverage`` - run tests and coverage using nose.
* ``paver analyze`` - run static analysis using flake8.
* ``paver sdist`` - generates setup. Used internally: see paver build.
* ``paver docs`` - clean docs folder and create HTML documentation.
* ``paver install`` - pip install picdb package [#puninst]_.
* ``paver uninstall`` - pip uninstall picdb package [#puninst]_.
* ``paver regenerate_spec`` - generate a new pyinstaller spec.
* ``paver build_app`` - run pyinstaller on existing spec file.
* ``paver clean`` - remove dist/ and build/ folders.
* ``paver clean_app`` - remove pyinstaller output from dist folder.
* ``paver build`` - orchestrate previous commands to create application bundle.
* ``paver deploy`` - mv application bundle to /Applications.



Dependency Graph
================

The dependencies of picdb modules are determined using *snakefood* [#snakefood]_.
*snakefood* is a set of tools which can be combined, e.g. via shell pipes.

*sfood* creates a file with the dependencies which is then processed by
*sfood-graph* to generate a graph representation and creating a dot-file
for processing with *graphviz*.

``paver dependencies`` uses these tools
to create *reports/picdb.pdf*, a graphical representation of the dependencies.


Application Bundle Creation
===========================

The resulting application bundle for macOS is created with *pyinstaller*.

*pyinstaller* evaluates the project and creates a *.spec* file for further
processing. It tries to detect all dependencies to other packages.
In some cases this is not possible. Then those packages need to be
specified manually.
The same is true for other file types like images and other resources.

Therefore the *.spec* file has to be manually extended after generation.

*PicDB.spec* is a specification file which contains all extensions to allow
building the app bundle.

If a new *PicDB.spec* needs to be generated make sure to take over the required
extensions from the archived version. The nect section described the required
extensions.

Required Extensions
-------------------

All resource files need to be listed as *'datas'* in the Analysis step of
*pyinstaller*.
Some packages are also not detected automatically.
The *tkinter* hooks of *pyinstaller* need to be patched to work on macOS if
the file system is case insensitive. The patched code is in the
*pyinstaller-hooks* folder.

So add following lines to Analysis::

  added_files = [('venv/lib/python3.5/site-packages/postgresql/lib/libsys.sql', 'postgresql/lib'),
                 ('picdb/resources/config_app.yaml', 'picdb/resources'),
                 ('picdb/resources/config_log.yaml', 'picdb/resources'),
                 ('picdb/resources/eye.gif', 'picdb/resources'),
                 ('picdb/resources/not_found.png', 'picdb/resources'),
                 ('picdb/resources/not_supported.png', 'picdb/resources')]

  datas=added_files,
  hiddenimports=['postgresql.types.io.builtins', 'PIL._tkinter_finder'],
  hookspath=['pyinstaller-hooks'],
  runtime_hooks=['pyinstaller-hooks/pyi_rth__tkinter.py'],

For the app bundle a name and an icon set are specified in PicDB.spec::

  app = BUNDLE(exe,
             name='PicDB.app',
             icon='Icon.icns',
             bundle_identifier=None)

Those are currently all extensions required after generation of a new
PicDB.spec file.

Test
****

Tests were written using *unittest* and *hypothesis*. Test may be run with *nose* or *pytest*.
All tests are in folder */test*.

Currently only tests for the ``RLUCache`` class are available. Most of the code
is UI or persistence related and therefore not nicely testable
via unit tests [#ut1]_.


The persistence test was written for SQLite and not adapted for PostgreSQL.
This should be possible after providing some database setup code.




.. rubric:: Footnotes

.. [#snakefood] http://furius.ca/snakefood/doc/snakefood-doc.html
.. [#puninst] may be deprecated. Not required anymore.
.. [#ut1] But a couple more tests would be helpful anyway.

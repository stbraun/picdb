#usr/bin/env bash

# prepare folder for build reports
mkdir reports

# setup virtual environment ...
python3 -m venv venv

# ... and activate it
source venv/bin/activate

# install required packages
pip install -r requirements.txt

# run sanity checks
flake8 --output-file reports/flake8.txt --benchmark --count --statistics picdb start_picdb.py

pylint --rcfile=resrc/pylintrc picdb > reports/pylint.txt

# run test and measure coverage
nosetests --with-coverage --cover-branches --cover-inclusive --with-xunit --xunit-file=reports/nosetests.xml --cover-html --cover-html-dir=reports/coverage --cover-xml --cover-xml-file=reports/coverage.xml test/

# build source distribution tarball
paver sdist

# install package ...
python setup.py install

# ... and generate documentation
cd docs
make html

# package documentation
cd build
zip -r ../../dist/docs.zip html

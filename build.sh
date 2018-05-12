#usr/bin/env bash

# prepare folder for build reports
mkdir reports

# setup virtual environment ...
python3 -m venv venv

# ... and activate it
source venv/bin/activate

# install required packages
pip install --upgrade pip
if pip install -r requirements.txt; then
    echo "======================";
    echo "requirements installed";
    echo "======================";
else
    exit 1;
fi

# run sanity checks
if flake8 --output-file reports/flake8.txt --benchmark --count --statistics picdb start_picdb.py; then
    echo "=====================";
    echo " sanity tests passed ";
    echo "=====================";
else
    echo "=====================";
    echo " sanity tests failed ";
    echo "=====================";
fi

if pylint --rcfile=resrc/pylintrc picdb > reports/pylint.txt; then
    echo "========================";
    echo " static analysis passed ";
    echo "========================";
else
    echo "========================";
    echo " static analysis failed ";
    echo "========================";
    exit 1;
fi

# run test and measure coverage
if nosetests --with-coverage --cover-branches --cover-inclusive --with-xunit --xunit-file=reports/nosetests.xml --cover-html --cover-html-dir=reports/coverage --cover-xml --cover-xml-file=reports/coverage.xml test/  > reports/nosetest.txt 2>&1; then
   echo "=============";
   echo "tests passed";
   echo "=============";
else
   exit 1;
fi

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

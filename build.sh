#!/usr/bin/env bash

# prepare folder for build reports
mkdir reports

if [ -z "$1" ]; then
    echo 'usage: build.sh <cmd>'
    exit 1;
fi

mk_venv() {
    # setup virtual environment ...
    if python3 -m venv venv; then
        echo "================================";
        echo " Virtual environment installed. ";
        echo "================================";
    else
        exit 1;
    fi
}

activate_venv() {
    # activate virtual environment
    echo "==================================";
    echo " Activate virtual environment ... ";
    echo "==================================";
    source venv/bin/activate;
}

install_requirements() {
    # install required packages
    pip install --upgrade pip
    if pip install -r requirements.txt; then
        echo "=========================";
        echo " Requirements installed. ";
        echo "=========================";
    else
        exit 1;
    fi
}


check_sources() {
    # run sanity checks
    if flake8 --output-file reports/flake8.txt --benchmark --count --statistics picdb start_picdb.py; then
        echo "======================";
        echo " Sanity tests passed. ";
        echo "======================";
    else
        echo "======================";
        echo " Sanity tests failed. ";
        echo "======================";

        exit 1;
    fi

    if pylint --rcfile=resrc/pylintrc picdb start_picdb.py | tee reports/pylint.txt; then
        echo "=========================";
        echo " Static analysis passed. ";
        echo "=========================";
    else
        echo "=========================";
        echo " Static analysis failed. ";
        echo "=========================";
        exit 1;
    fi
}

run_tests() {
    # run test and measure coverage
    if nosetests --with-coverage --cover-branches --cover-inclusive --with-xunit --xunit-file=reports/nosetests.xml --cover-html --cover-html-dir=reports/coverage --cover-xml --cover-xml-file=reports/coverage.xml test/  > reports/nosetest.txt 2>&1; then
       echo "===============";
       echo " Tests passed. ";
       echo "===============";
    else
       exit 1;
    fi
}

create_doc() {
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
}

build_app() {
    # build the app for deployment
    rm -rf dist/PicDB dist/PicDB.app;
    echo "=====================================";
    echo " Building the application bundle ... ";
    echo "=====================================";
    pyinstaller PicDB.spec;
}

case "$1" in
    venv )
        mk_venv;
        ;;
    requ )
        activate_venv;
        install_requirements;
        ;;
    checks )
        activate_venv;
        check_sources;
        ;;
    tests )
        activate_venv;
        run_tests;
        ;;
    doc )
        activate_venv;
        create_doc;
        ;;
    build )
        activate_venv;
        build_app;
        ;;
    all )
        mk_venv;
        activate_venv;
        install_requirements;
        check_sources;
        run_tests;
        create_doc;
        build;
        ;;
esac
exit 0

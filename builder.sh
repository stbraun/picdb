#!/usr/bin/env bash

# export PATH=/usr/local/bin:/usr/local/sbin:$PATH

# prepare folder for build reports
if [ ! -d reports ]; then
    mkdir reports
fi

if [ -z "$1" ]; then
    $1 = "help"
fi

mk_venv() {
    # setup virtual environment ...
    echo " ===> skip mk_venv "
#    if pipenv install; then
#        echo "================================";
#        echo " Virtual environment installed. ";
#        echo "================================";
#    else
#        exit 1;
#    fi
}

activate_venv() {
    # activate virtual environment
     echo " ===>  skip activate_venv "
#    echo "==================================";
#    echo " Activate virtual environment ... ";
#    echo "==================================";
    # pipenv shell
}

install_requirements() {
    # install required packages
    pip install --upgrade pip
    if pipenv install --dev; then
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

    if pylint --rcfile=resrc/pylintrc --output-format=parseable picdb start_picdb.py | tee reports/pylint.txt; then
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
    if pytest --junit-xml=reports/unittest.xml --doctest-modules --cov=picdb/ --cov-branch --cov-report=xml:reports/coverage.xml --cov-report=html:reports/coverage test; then
       echo "===============";
       echo " Tests passed. ";
       echo "===============";
    else
       exit 1;
    fi
}

create_doc() {
    # build source distribution tarball
    python setup.py sdist

    # install package ...
    python setup.py install

    # ... and generate documentation
    pushd docs
    make html

    # package documentation
    pushd build
    zip -r ../../dist/docs.zip html
    popd
    popd

}

source_dist() {
    # build source distribution tarball
    python setup.py sdist
}

build_app() {
    # build the app for deployment
    rm -rf dist/PicDB dist/PicDB.app;
    echo "=====================================";
    echo " Building the application bundle ... ";
    echo "=====================================";
    if PyInstaller PicDB.spec; then
    echo "========================================";
    echo " Building application bundle succeeded. ";
    echo "========================================";
    else
    echo "=====================================";
    echo " Building application bundle failed. ";
    echo "=====================================";
       exit 1;
    fi
}

clean_env() {
    rm -rf build dist picdb.egg-info;
    rm -rf __pycache__ test/__pycache__ picdb/__pycache__ scripts/__pycache__;
    rm -rf .coverage coverage.xml reports/* docs/build/*;
    find picdb test -name "*.pyc" -exec rm {} ";";
}

case "$1" in
    clean )
        clean_env;
        ;;
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
    sdist )
        activate_venv;
        source_dist;
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
        source_dist;
        build_app;
        create_doc;
        ;;
    *   )
        echo "builder.sh [clean | venv | requ | checks | tests | doc | sdist | build | all]"
esac
exit 0

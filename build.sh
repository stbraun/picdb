#usr/bin/env bash

source venv/bin/activate

pip install -r requirements.txt

flake8 --output-file reports/flake8.txt --benchmark --count --statistics picdb start_picdb.py

nosetests --with-coverage --cover-branches --cover-inclusive --cover-html --cover-html-dir=reports/coverage --cover-xml --cover-xml-file=reports/coverage.xml test/

paver docs

paver sdist

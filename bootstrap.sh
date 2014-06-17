#!/bin/bash

requirements="fabric fabtools"

if [[ "$VIRTUAL_ENV" == "" ]]; then
    curl -o - https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
    curl -o - https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python -

fi

pip install -U $requirements

echo "Done. Please run: fab -H user@host:ip install"

#!/bin/bash
# Build from scratch and run unit tests from python 2.6 and python 3.1
# Then run doctests to verify doc examples
# Note: requires nose

error=0

rm -rf build

echo "************"
echo " Python 2.6"
echo "************"
echo
python setup.py build && \
nosetests -d -w build/lib.*2.6/planar/ --with-coverage || error=1

echo
echo "************"
echo " Python 3.1"
echo "************"
echo
python3 setup.py build && \
nosetests3 -d -w build/lib.*3.1/planar/ --with-coverage || error=1

echo
echo -n "Doctests... "
python3 -m doctest doc/source/*.rst && echo "passed." || error=1

exit $error

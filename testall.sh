#!/bin/bash
# Build from scratch and run unit tests from python 2.6, 2.7, 3.1
# Then run doctests to verify doc examples
# Note: requires nose installed in each python instance

error=0

rm -rf build

for ver in 2.6 2.7 3.1; do
	echo "************"
	echo " Python $ver"
	echo "************"
	echo
	if which python${ver}; then
		# pass in -UNDEBUG to ensure assertions are enabled in C-extensions
		SETUP_PY_CFLAGS="-UNDEBUG" python${ver} setup.py build && \
		python${ver} -m nose.core \
			-d -w build/lib.*${ver}/ --with-coverage --cover-erase $@ || error=1
	else
		echo >&2 "!!! Python ${ver} not found !!!"
		error=1
	fi
done

echo
echo -n "Doctests... "
srcdir=`pwd`
cd build/lib.*3.?/ && python3 -m doctest ${srcdir}/doc/source/*.rst && echo "OK" || error=1

exit $error

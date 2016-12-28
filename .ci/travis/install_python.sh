#! /bin/bash

PREFIX=$1
if [[ $PREFIX == "" ]]; then
  PREFIX=$HOME/miniconda
fi

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
  OS="MacOSX-x86_64";
else
  OS="Linux-x86_64";
fi
if [[ "$TRAVIS_PYTHON_VERSION" == 2.* ]]; then
  wget http://repo.continuum.io/miniconda/Miniconda-latest-$OS.sh -O miniconda.sh;
else
  wget http://repo.continuum.io/miniconda/Miniconda3-latest-$OS.sh -O miniconda.sh;
fi
bash miniconda.sh -b -p $PREFIX
export PATH="$PREFIX/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda install python=$TRAVIS_PYTHON_VERSION
conda install -q conda-build
conda install -q anaconda-client
conda install -q coverage
conda install -q sphinx

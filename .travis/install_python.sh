#! /bin/bash

OS="Linux-x86_64"

if [[ "$TRAVIS_PYTHON_VERSION" == 2.* ]]; then
  wget http://repo.continuum.io/miniconda/Miniconda-3.4.2-$OS.sh -O miniconda.sh;
else
  wget http://repo.continuum.io/miniconda/Miniconda3-3.4.2-$OS.sh -O miniconda.sh;
fi
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update conda
conda info -a
cat requirements.txt | xargs conda create -n test-env python=$TRAVIS_PYTHON_VERSION
source activate test-env

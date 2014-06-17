#! /usr/bin/bash

OS=Linux
BASE_DIR=$HOME
cd $BASE_DIR

git archive --remote=git://git.code.sf.net/p/esmfcontrib/ESMPy --format=tar --prefix=ESMPy/ 630r_01b | tar xf -
export ESMF_DIR=$BASE_DIR/esmf
export ESMFMKFILE=$BASE_DIR/_inst/lib/libO/$OS.gfortran.64.mpiuni.default/esmf.mk

export PATH="$HOME/miniconda/bin:$PATH"
source activate test-env

echo "PYTHON=$(which python)"
echo "ESMF_DIR=$ESMF_DIR"
echo "ESMFMKFILE=$ESMFMKFILE"
echo $(ls -l $ESMFMKFILE)

cd ESMPy
python setup.py build install
#! /usr/bin/bash

OS=Linux
BASE_DIR=$HOME

git archive --remote=git://git.code.sf.net/p/esmfcontrib/ESMPy --format=tar --prefix=ESMPy/ 630r_01b | tar xf -
export ESMF_DIR=$BASE_DIR/esmf
export ESMFMKFILE=$ESMF_DIR/_inst/lib/libO/$OS.gfortran.64.mpiuni.default/esmf.mk

cd ESMPy
sudo python setup.py build install
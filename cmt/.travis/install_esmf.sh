#! /bin/bash

BASE_DIR=$HOME

cd $BASE_DIR
git archive --remote=git://git.code.sf.net/p/esmf/esmf --format=tar --prefix=esmf/ ESMF_6_3_0r | tar xf -
export ESMF_DIR=$BASE_DIR/esmf
export ESMF_COMPILER=gfortran
cd $ESMF_DIR && make
sudo make install
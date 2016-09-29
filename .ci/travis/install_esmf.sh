#! /bin/bash

BASE_DIR=$HOME

cd $BASE_DIR
git archive --remote=git://git.code.sf.net/p/esmf/esmf --format=tar --prefix=esmf/ ESMF_6_3_0r | tar xf -

export ESMF_DIR=$BASE_DIR/esmf
export ESMF_COMPILER=gfortran
export ESMF_INSTALL_PREFIX=$BASE_DIR/_inst

echo "ESMF_DIR=$ESMF_DIR"
echo "ESMF_COMPILER=$ESMF_COMPILER"
echo "ESMF_INSTALL_PREFIX=$ESMF_INSTALL_PREFIX"

cd $ESMF_DIR
make -j4 || echo "unable to make ESMF"
make -j4 install || echo "unable to install ESMF"

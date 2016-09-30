#!/bin/bash

PACKAGE_NAME=$1

PREFIX=$(python -c "import sys; print(sys.prefix)")
ANACONDA=$(which anaconda)

if [[ $ANACONDA_TOKEN == "" ]]; then
  ANACONDA_UPLOAD="$ANACONDA upload"
else
  ANACONDA_UPLOAD="$ANACONDA -t $ANACONDA_TOKEN upload"
fi

if [[ "$TRAVIS_TAG" == v* ]]; then
  export CHANNEL="main"
else
  export CHANNEL="dev"
fi

echo "Uploading to $CHANNEL"
echo $ANACONDA_UPLOAD --force --user csdms --channel $CHANNEL $PREFIX/conda-bld/**/$PACKAGE_NAME*bz2
$ANACONDA_UPLOAD --force --user csdms --channel $CHANNEL \
  $PREFIX/conda-bld/**/$PACKAGE_NAME*bz2

echo "Done."

#! /usr/bin/env python

from __future__ import print_function

import sys

from cmt.scanners import (InputParameterScanner, CmtScanner,
                          MissingKeyError)

def main ():
    import argparse

    parser = argparse.ArgumentParser (description='Parse CSDMS parameter annotation')
    parser.add_argument ('file', nargs='+')

    args = parser.parse_args ()

    if len (args.file) == 1:
        with open (args.file[0], 'r') as f:
            scanner = InputParameterScanner (f)
            scanner.scan_file ()
            print (scanner.contents ())
    else:
        for file in args.file:
            with open (file, 'r') as f:
                scanner = InputParameterScanner (f)
                scanner.scan_file ()

            out_file = scanner.find ('file')

            assert (len (out_file) <= 1)
            out_file = out_file[0] + '.in'

            print ('Writing template file %s...' % out_file)
            try:
                with open (out_file, 'w') as f:
                    f.write (scanner.contents ())
            except IndexError:
                print (scanner.contents ())

if __name__ == '__main__':
    main ()


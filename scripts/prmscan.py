#! /usr/bin/env python

from __future__ import print_function

import sys

from cmt.scanners import (InputParameterScanner, CmtScanner,
                          MissingKeyError)

def main ():
    import argparse

    parser = argparse.ArgumentParser (description='Parse CSDMS parameter annotation')
    parser.add_argument ('file', type=argparse.FileType ('r'))
    parser.add_argument ('--format', choices=['raw', 'cmt', 'fill'], default='raw',
                         help='Output format')

    args = parser.parse_args ()

    if args.format in ['raw', 'fill']:
        scanner = InputParameterScanner (args.file)
    elif args.format == 'cmt':
        scanner = CmtScanner (args.file)
    scanner.scan_file ()

    if args.format == 'fill':
        try:
            print (scanner.fill_contents ())
        except MissingKeyError as e:
            print ('ERROR: Missing key for %s in prm file.' % e, sys.stderr)
    else:
        print (scanner.to_xml ())

if __name__ == '__main__':
    main ()


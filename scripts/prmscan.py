#! /usr/bin/env python

from __future__ import print_function

import sys

from cmt.scanners import (InputParameterScanner, CmtScanner,
                          MissingKeyError)

def main ():
    import argparse

    parser = argparse.ArgumentParser (description='Parse CSDMS parameter annotation')
    parser.add_argument ('file', type=argparse.FileType ('r'), nargs='+')
    parser.add_argument ('--format', choices=['raw', 'cmt', 'fill'], default='raw',
                         help='Output format')

    args = parser.parse_args ()

    scanners = []
    for file in args.file:
        if args.format in ['raw', 'fill']:
            scanner = InputParameterScanner (file)
        elif args.format == 'cmt':
            scanner = CmtScanner (file)

        scanner.scan_file ()

        scanners.append (scanner)

    root = scanners[0]
    for scanner in scanners[1:]:
        root.update (scanner)

    if args.format == 'fill':
        try:
            print (root.fill_contents ())
        except MissingKeyError as e:
            print ('ERROR: Missing key for %s in prm file.' % e, sys.stderr)
    else:
        print (root.to_xml ())

if __name__ == '__main__':
    main ()


#! /usr/bin/env python

from __future__ import print_function

import sys

from cmt.scanners import (InputParameterScanner, CmtScanner,
                          MissingKeyError)

def main ():
    import argparse

    parser = argparse.ArgumentParser (description='Parse CSDMS parameter annotation')
    parser.add_argument ('file', type=argparse.FileType ('r'), nargs='+')
    parser.add_argument ('-o', '--output', type=argparse.FileType ('w'), default='-')
    parser.add_argument ('--format', choices=['raw', 'cmt'], default='raw',
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

    print (root.to_xml (), file=args.output)

if __name__ == '__main__':
    main ()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json

runPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(runPath, ".."))
from lib.cpeguesser import CPEGuesser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find potential CPE names from a list of keyword(s) and return a JSON of the results')
    parser.add_argument('--word', help='One or more keyword(s) to lookup', action='append')
    args = parser.parse_args()

    if args.word is None:
        print("Missing keyword(s)")
        parser.print_help()
        sys.exit(1)

    cpeGuesser = CPEGuesser()
    print(json.dumps(cpeGuesser.guessCpe(args.word)))

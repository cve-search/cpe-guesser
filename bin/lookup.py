#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json

runPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(runPath, ".."))
from lib.cpeguesser import CPEGuesser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find potential CPE names from a list of keyword(s) and return a JSON of the results"
    )
    parser.add_argument(
        "word",
        metavar="WORD",
        type=str,
        nargs="+",
        help="One or more keyword(s) to lookup",
    )
    args = parser.parse_args()

    cpeGuesser = CPEGuesser()
    print(json.dumps(cpeGuesser.guessCpe(args.word)))

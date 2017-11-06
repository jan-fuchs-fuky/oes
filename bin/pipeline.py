#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Author: Jan Fuchs <fuky@asu.cas.cz>
#

import os
import sys
import argparse

from glob import glob
from pyraf import iraf

SCRIPT_PATH = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
sys.path.append(SCRIPT_PATH)

class Pipeline:
    def __init__(self, args):
        self.args = args

    def run(self):
        self.make_mzero()
        self.make_mcomp()

    @staticmethod
    def make_mzero():
        pass

    @staticmethod
    def make_mcomp():
        pass

    @staticmethod
    def imcombine(input_list, output_filename):
        input_filename = os.path.join(SCRIPT_PATH, "../tmp/imcombine.input")

        with open(input_filename, "w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")

        iraf.imcombine("@%s" % input_filename, output_filename, combine="median")

def main():
    parser = argparse.ArgumentParser(
        description="OES pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="See https://github.com/jan-fuchs-fuky/oes for more info.")

    parser.add_argument("-i", "--input-dir", required=True, help="path to OES night")
    parser.add_argument("-o", "--output-dir", default="/tmp/oes", help="path to output directory")

    args = parser.parse_args()

    pipeline = Pipeline(args)
    pipeline.run()

if __name__ == '__main__':
    main()

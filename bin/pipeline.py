#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Author: Jan Fuchs <fuky@asu.cas.cz>
#
# http://iraf.noao.edu/docs/spectra.html
# http://stelweb.asu.cas.cz/~slechta/odbzajem.html
# http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?instruments
#

import os
import sys
import argparse

from glob import glob
from pyraf import iraf

#iraf.noao.imutil()
iraf.noao.imred()
iraf.noao.imred.ccdred()
iraf.noao.imred.crutil()
iraf.noao.imred.echelle()

SCRIPT_PATH = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
sys.path.append(SCRIPT_PATH)

class Pipeline:
    def __init__(self, args):
        self.args = args

    def run(self):
        input_pathname = os.path.join(self.args.input_dir, "zero/*.fit")
        output_filename = os.path.join(self.args.output_dir, "mzero.fit")

        self.zerocombine(input_pathname, output_filename)

    @staticmethod
    def imcombine(input_pathname, output_filename):
        input_list = glob(input_pathname)
        input_filename = os.path.join(SCRIPT_PATH, "../tmp/imcombine.input")

        with open(input_filename, "w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")

        iraf.imcombine("@%s" % input_filename, output_filename, combine="median")

    @staticmethod
    def zerocombine(input_pathname, output_filename):
        input_list = glob(input_pathname)
        input_filename = os.path.join(SCRIPT_PATH, "../tmp/zerocombine.input")

        with open(input_filename, "w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")

        iraf.noao.imred.ccdred.zerocombine(input="@%s" % input_filename, output=output_filename, combine="median")

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

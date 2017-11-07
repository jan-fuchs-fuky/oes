#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Author: Jan Fuchs <fuky@asu.cas.cz>
#
# http://iraf.noao.edu/docs/spectra.html
# http://stelweb.asu.cas.cz/~slechta/odbzajem.html
#
# http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?imarith
# http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?instruments
#

import os
import sys
import time
import argparse

from glob import glob
from pyraf import iraf

iraf.images()
iraf.images.imutil()

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

        input_pathname = os.path.join(self.args.input_dir, "flat/*.fit")
        self.process_flats(input_pathname)

    @staticmethod
    def imcombine(input_pathname, output_filename):
        input_list = glob(input_pathname)
        input_filename = os.path.join(SCRIPT_PATH, "../tmp/imcombine.input")

        with open(input_filename, "w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")

        iraf.imcombine("@%s" % input_filename, output_filename, combine="median")

    # TODO: umoznit beh vice instaci tj. generovat jedinecny nazev pro zerocombine.input a po
    # akci ho mazat (stejne tak u fce imcombine())
    @staticmethod
    def zerocombine(input_pathname, output_filename):
        input_list = glob(input_pathname)
        input_filename = os.path.join(SCRIPT_PATH, "../tmp/zerocombine.input")

        with open(input_filename, "w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")

        iraf.noao.imred.ccdred.zerocombine(input="@%s" % input_filename, output=output_filename, combine="median")

    @staticmethod
    def process_flats(input_pathname):
        input_list = glob(input_pathname)
        input_filename = os.path.join(SCRIPT_PATH, "../tmp/flat_mzero.input")
        output_filename = os.path.join(SCRIPT_PATH, "../tmp/flat_mzero.output")

        output_list = []
        for item in input_list:
            filename = os.path.basename(item)
            filename = os.path.join("/tmp/oes", "z_%s" % filename)
            output_list.append(filename)

        with open(input_filename, "w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")

        with open(output_filename, "w") as fo:
            fo.write("\n".join(output_list))
            fo.write("\n")

        iraf.images.imutil.imarith(
            operand1="@%s" % input_filename,
            op='-',
            operand2="/tmp/oes/mzero.fit",
            result="@%s" % output_filename)

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

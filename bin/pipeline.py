#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Author: Jan Fuchs <fuky@asu.cas.cz>
#
# http://iraf.noao.edu/docs/spectra.html
# http://stelweb.asu.cas.cz/~slechta/odbzajem.html
#
# http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?instruments
#

import os
import sys
import time
import tempfile
import argparse

from glob import glob
from pyraf import iraf

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

        with tempfile.NamedTemporaryFile(mode="w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")
            fo.flush()

            iraf.imcombine("@%s" % fo.name, output_filename, combine="median")

    # TODO: umoznit beh vice instaci tj. generovat jedinecny nazev pro zerocombine.input a po
    # akci ho mazat (stejne tak u fce imcombine())
    @staticmethod
    def zerocombine(input_pathname, output_filename):
        input_list = glob(input_pathname)

        with tempfile.NamedTemporaryFile(mode="w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")
            fo.flush()

            iraf.noao.imred.ccdred.zerocombine(input="@%s" % fo.name, output=output_filename, combine="median")

    @staticmethod
    def process_flats(input_pathname):
        input_list = glob(input_pathname)

        output_list = []
        for item in input_list:
            filename = os.path.basename(item)
            filename = os.path.join("/tmp/oes", "z_%s" % filename)
            output_list.append(filename)

        with tempfile.NamedTemporaryFile(mode="w") as fo:
            fo.write("\n".join(input_list))
            fo.write("\n")
            fo.flush()

            with tempfile.NamedTemporaryFile(mode="w") as z_fo:
                z_fo.write("\n".join(output_list))
                z_fo.write("\n")
                z_fo.flush()

                # http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?imarith
                iraf.images.imutil.imarith(
                    operand1="@%s" % fo.name,
                    op='-',
                    operand2="/tmp/oes/mzero.fit",
                    result="@%s" % z_fo.name,
                )

                output_list = []
                for item in input_list:
                    filename = os.path.basename(item)
                    filename = os.path.join("/tmp/oes", "zc_%s" % filename)
                    output_list.append(filename)

                with tempfile.NamedTemporaryFile(mode="w") as zc_fo:
                    zc_fo.write("\n".join(output_list))
                    zc_fo.write("\n")
                    zc_fo.flush()

                    # http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?cosmicrays.hlp
                    # iraf.noao.imred.crutil.cosmicrays.lParam()
                    iraf.noao.imred.crutil.cosmicray(
                        input="@%s" % z_fo.name,
                        output="@%s" % zc_fo.name,
                        fluxratio=10,
                        window="7",
                        interactive="no",
                    )

def main():
    parser = argparse.ArgumentParser(
        description="OES pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="See https://github.com/jan-fuchs-fuky/oes for more info.")

    parser.add_argument("-i", "--input-dir", required=True, help="path to OES night")
    parser.add_argument("-o", "--output-dir", default="/tmp/oes", help="path to output directory")

    args = parser.parse_args()

    if os.listdir(args.output_dir):
        print("ERROR: Output directory '%s' must be empty" % args.output_dir)
        sys.exit()

    iraf.images()
    iraf.images.imutil()

    iraf.noao.imred()
    iraf.noao.imred.ccdred()
    iraf.noao.imred.crutil()
    iraf.noao.imred.echelle()
    iraf.noao.imred.crutil()

    pipeline = Pipeline(args)
    pipeline.run()

if __name__ == '__main__':
    main()

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Author: Jan Fuchs <fuky@asu.cas.cz>
#
# Depends: libpython3.4-minimal, python3-astropy, python3-pyfits, libpython3.4-stdlib
#

import os
import argparse
import pyfits

from astropy.time import Time

class AddJD:

    def __init__(self, args):
        self.args = args

        for root, dirs, files in os.walk(args.input_dir):
            for name in files:
                if name.endswith(".fit"):
                    filename = os.path.join(root, name)
                    self.process(filename)

    def process(self, filename):
        self.add_jd(filename)

    @staticmethod
    def add_jd(filename):
        hdulist = pyfits.open(filename, mode="update", memmap=True)
        prihdr = hdulist[0].header

        date_time_str = "%s %s" % (prihdr["DATE-OBS"], prihdr["UT"])
        astro_time = Time(date_time_str, format="iso", scale="utc")

        print("Add JD %s (%s) to %s" % (astro_time.jd, date_time_str, filename))

        prihdr["JD"] = astro_time.jd

        hdulist.close()

def main():
    parser = argparse.ArgumentParser(
        description="Add JD to FITS file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="See https://github.com/jan-fuchs-fuky/oes for more info.")

    parser.add_argument("-i", "--input-dir", required=True, help="path to *.fit")

    args = parser.parse_args()

    AddJD(args)

if __name__ == '__main__':
    main()

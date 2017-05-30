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
import shutil

from astropy.time import Time
from glob import glob

class ImportFits:

    def __init__(self, args):
        self.args = args

        if (args.year is None):
            pattern = "%s/20*/*/*.fit" % args.input_dir
        elif (args.month is None):
            pattern = "%s/%04i/*/*.fit" % (args.input_dir, args.year)
        elif (args.day is None):
            pattern = "%s/%04i/%04i%02i*/*.fit" % (args.input_dir, args.year, args.year, args.month)
        else:
            pattern = "%s/%04i/%04i%02i%02i/*fit" % (args.input_dir, args.year, args.year, args.month, args.day)

        if __debug__:
            print("args = %s" % args.__dict__)
            print("pattern = %s" % pattern)

        for filename in glob(pattern):
            self.import_fits(filename)

    def import_fits(self, filename):
        print("=== Processing %s ===" % filename)

        image_type = self.get_image_type(filename)
        night = os.path.basename(os.path.dirname(filename))
        dst_dir = os.path.join(self.args.output_dir, night, image_type)

        print("mkdir %s" % dst_dir)
        os.makedirs(dst_dir, exist_ok=True)

        print("copy %s %s" % (filename, dst_dir))
        shutil.copy(filename, dst_dir)

        dst_filename = os.path.join(dst_dir, os.path.basename(filename))

        self.add_jd(dst_filename)

    @staticmethod
    def get_image_type(filename):
        hdulist = pyfits.open(filename, mode="readonly", memmap=True)
        prihdr = hdulist[0].header

        if (prihdr["IMAGETYP"] in ["comp", "flat", "zero", "dark"]):
            image_type = prihdr["IMAGETYP"]
        elif (prihdr["IMAGETYP"] == "object"):
            if (prihdr["OBJECT"] == "domeflat"):
                image_type = "domeflat"
            else:
                image_type = prihdr["IMAGETYP"]
        else:
            raise Exception("Unknown IMAGETYP: '%s'" % prihdr["IMAGETYP"])

        hdulist.close()

        return image_type

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
    parser = argparse.ArgumentParser(description="Importing FITS file.")

    parser.add_argument("-i", "--input-dir", default="/i/data2m/OES")
    parser.add_argument("-o", "--output-dir", default="/tmp/oes")
    parser.add_argument("-y", "--year", type=int)
    parser.add_argument("-m", "--month", type=int)
    parser.add_argument("-d", "--day", type=int)

    args = parser.parse_args()

    ImportFits(args)

if __name__ == '__main__':
    main()

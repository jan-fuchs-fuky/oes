#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Author: Jan Fuchs <fuky@asu.cas.cz>
#
# Depends: libpython3.4-minimal, python3-astropy, libpython3.4-stdlib
#

import os
import sys
import argparse
import shutil

from astropy.io import fits
from astropy.time import Time
from glob import glob
from subprocess import Popen, PIPE
from datetime import datetime, timedelta

class ImportFits:

    def __init__(self, args):
        self.args = args

        if args.actual:
            dt = datetime.now() - timedelta(days=1)
            args.year = dt.year
            args.month = dt.month
            args.day = dt.day

        if (args.year is None):
            pattern = "%s/20*/*" % args.input_dir
        elif (args.month is None):
            pattern = "%s/%04i/*" % (args.input_dir, args.year)
        elif (args.day is None):
            pattern = "%s/%04i/%04i%02i*" % (args.input_dir, args.year, args.year, args.month)
        else:
            pattern = "%s/%04i/%04i%02i%02i*" % (args.input_dir, args.year, args.year, args.month, args.day)

        find_cmd = "find %s -path '%s' -name '*.fit' -printf '%%P\\0'" % (args.input_dir, pattern)

        remote_rsync = ""
        if (args.remote):
            find_cmd = "ssh %s \"%s\"" % (args.remote, find_cmd)
            remote_rsync = "%s:" % args.remote

        cmd = []
        cmd.append(find_cmd)
        cmd.append("rsync -0t --files-from=- %s%s %s" % (remote_rsync, args.input_dir, args.output_dir))

        cmd = " |".join(cmd)

        if __debug__:
            print("args = %s" % args.__dict__)
            print("pattern = %s" % pattern)
            print("cmd = %s" % cmd)

        pipe = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = pipe.communicate()

        if (pipe.returncode != 0):
           print("rsync stdout = %s" % stdout)
           print("rsync stderr = %s" % stderr)
           sys.exit(1)

        pattern = "%s/*/*/*.fit" % (args.output_dir)

        for filename in glob(pattern):
            self.import_fits(filename)

    def import_fits(self, filename):
        print("=== Processing %s ===" % filename)

        fits_header = self.get_fits_header(filename)

        dst_dir = os.path.join(os.path.dirname(filename), fits_header["image_type"])
        if (fits_header["image_type"] == "object"):
            dst_dir = os.path.join(dst_dir, fits_header["object"])

        dst_filename = os.path.join(dst_dir, os.path.basename(filename))

        print("mkdir %s" % dst_dir)
        os.makedirs(dst_dir, exist_ok=True)

        print("move %s %s" % (filename, dst_filename))
        shutil.move(filename, dst_filename)

        self.add_jd(dst_filename)

    @staticmethod
    def get_fits_header(filename):
        hdulist = fits.open(filename, mode="readonly", memmap=True)
        prihdr = hdulist[0].header

        fits_header = {}
        fits_header["object"] = prihdr["OBJECT"].strip().replace(" ", "_")

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

        fits_header["image_type"] = image_type

        return fits_header

    @staticmethod
    def add_jd(filename):
        hdulist = fits.open(filename, mode="update", memmap=True)
        prihdr = hdulist[0].header

        date_time_str = "%s %s" % (prihdr["DATE-OBS"], prihdr["UT"])
        astro_time = Time(date_time_str, format="iso", scale="utc")

        print("Add JD %s (%s) to %s" % (astro_time.jd, date_time_str, filename))

        prihdr["JD"] = astro_time.jd

        hdulist.close()

def main():
    parser = argparse.ArgumentParser(
        description="Importing FITS file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="See https://github.com/jan-fuchs-fuky/oes for more info.")

    parser.add_argument("-i", "--input-dir", default="/i/data2m/OES", help="path to OES data")
    parser.add_argument("-o", "--output-dir", default="/tmp/oes", help="path to output directory")
    parser.add_argument("-y", "--year", type=int)
    parser.add_argument("-m", "--month", type=int)
    parser.add_argument("-d", "--day", type=int)
    parser.add_argument("-a", "--actual", action="store_true")
    parser.add_argument("-r", "--remote", metavar="USER@HOST", default="", help="download OES data from remote computer over SSH")

    args = parser.parse_args()

    ImportFits(args)

if __name__ == '__main__':
    main()

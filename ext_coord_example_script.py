#!/usr/bin/python3

import argparse
import glob

from project import coordgaus as cgauss

outfiles_parser = argparse.ArgumentParser(description='Get coordinates from Gaussian .log and return them in '
                                                      '.xyz, .com, and/or LaTeX-type format using the `coordgaus` '
                                                      'library. ')
outfiles_parser.add_argument('WORKDIR',
                             metavar='working_directory',
                             type=str,
                             help='The path where the files are.')


outfiles_parser.add_argument('-f',
                             metavar='file_type',
                             type=str,
                             default='.log',
                             help='The type of file to be parsed, e.g., .log')


args = outfiles_parser.parse_args()

WORKDIR = args.WORKDIR
FILES_PATH = WORKDIR + '*' + args.f


def get_outfiles(DIR):
    """Gets the file paths from which the 3PA info will be extracted.
    """

    file_paths = glob.glob(DIR, recursive=True)

    return file_paths


outfiles = get_outfiles(FILES_PATH)
for file in outfiles:

    file_xyz = cgauss.XFile(file, WORKDIR_PATH=WORKDIR)
    file_xyz.get_xyz()

    new_file_2 = cgauss.GaInpFile(file, WORKDIR_PATH=WORKDIR)
    new_file_2.get_gainp()

    file_si = cgauss.SupInfFile(file, WORKDIR_PATH=WORKDIR)
    file_si.get_si()



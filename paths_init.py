# standard modules
import os
import argparse

'''
Module to setup important paths and filenames
for the sanity checker. It contains:

    - write_path: write the file "paths.py" based on user input

    -abs_path: duplicate from module utils.py

C.Siegenthaler 07.2020 (C2SM)
J.Jucker 01.2021 (C2SM)

'''

def write_path(p_raw_files, \
               p_ref_csv_files,\
               p_stages,\
               p_wrkdir,\
               p_f_vars_proc):

    # make all paths absolute
    p_raw_files = abs_path(p_raw_files)
    p_ref_csv_files = abs_path(p_ref_csv_files)
    p_stages = abs_path(p_stages)
    p_wrkdir = abs_path(p_wrkdir)
    p_f_vars_proc = abs_path(p_f_vars_proc)

    # open the file
    fp=open('lib/paths.py','w')

    # write out paths
    fp.write('rootdir = "{}"\n'.format(os.getcwd()))
    fp.write('p_raw_files = "{}"\n'.format(p_raw_files))
    fp.write('p_ref_csv_files = "{}"\n'.format(p_ref_csv_files))
    fp.write('p_stages = "{}"\n'.format(p_stages))
    fp.write('p_wrkdir = "{}"\n'.format(p_wrkdir))
    fp.write('p_f_vars_proc = "{}"\n'.format(p_f_vars_proc))

    # close file
    fp.close()

    return()

def abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        path = os.path.abspath(path)
        return path

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--p_raw_files','-pr', dest='p_raw_files', \
                        required=True, \
                        help='Path to the raw files of the new experiments (mandatory)')

    parser.add_argument('--p_ref_csv_files',dest='p_ref_csv_files', \
                        default='ref/echam-hammoz', \
                        help='Relative or absolute path to the pool of reference csv-files')

    parser.add_argument('--p_stages',dest='p_stages', \
                        default='stages', \
                        help='Relative or absolute path to the folder to store results of the different processing stages (needs disk space)')

    parser.add_argument('--p_wrkdir', dest='p_wrkdir', \
                        default='wrkdir', \
                        help='Relative or absolute path to the working directory (needs disk space)')

    parser.add_argument('--p_f_vars_proc',dest='p_f_vars_proc',\
                        default='variables_to_process', \
                        help='Relative or absolute path to folder containig variables to process for each test')

    args = parser.parse_args()

    write_path(p_raw_files     = args.p_raw_files, \
               p_ref_csv_files = args.p_ref_csv_files, \
               p_stages        = args.p_stages, \
               p_wrkdir        = args.p_wrkdir,\
               p_f_vars_proc   = args.p_f_vars_proc)

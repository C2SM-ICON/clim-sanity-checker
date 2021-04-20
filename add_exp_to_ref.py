# standard modules
import os
import shutil
import argparse

# aliased standard modules
import pandas as pd

# modules of sanity checker
import lib.paths as paths
import lib.utils as utils
import lib.logger_config as logger_config

# standalone imports
from lib.logger_config import log
from lib.test_config import get_config_of_current_test
from lib.color import Style

'''
Module providing the functionality to add an experiment
to the reference pool. It contains:

    - add_line_descr_f: Add a new line to the experiment description file
            with all information about an experiment

    - main: asks user for additional information about experiment, commits 
        data of new experiment to git-repository

        Help: python add_exp_tp_ref.py --help

C.Siegenthaler 07.2020 (C2SM)
J.Jucker 01.2021 (C2SM)

'''


def add_line_descr_f(exp,f_exp_descr):
    '''
    Add line for exp exp in file f_exp_descr

    :param exp: new expirement name
    :param f_exp_descr: file in which the new line has to be added

    return: None
    '''

    log.info('Adding line {} in the file {}:'.format(exp,f_exp_descr))

    # open file in dataframe
    if not os.path.isfile(f_exp_descr):
        # create dataframe
        cols_exp_descr_f = ['Experiment name',
                            'Platform',
                            'OS',
                            'Compiler (with version)',
                            'Optimisation level (-OX)',
                            '-fast-transcendentals (y/n)',
                            '-no-prec-sqrt (y/n)',
                            '-no-prec-div (y/n)',
                            'welch (y/n)',
                            'fldcor (y/n)',
                            'rmse (y/n)',
                            'emi (y/n)',
                            'Date of experiment (month yyyy)']
        df_exp_descr = pd.DataFrame(columns=cols_exp_descr_f)
    else:
        df_exp_descr = pd.read_csv(f_exp_descr, sep=';')

    # collect information from user
    log.banner('Please give the following informations '
               'about your experiment')
    dict_line = {'Experiment name': exp}
    for col_name in df_exp_descr.keys():

        if col_name != 'Experiment name':

            # ask the user for info
            dict_line[col_name] = input('{} : '.format(col_name))

    # amend the information if needed
    while True:

        # new dataframe containing new line for exp
        df_exp_descr_new = df_exp_descr.append(dict_line, ignore_index=True)

        log.banner('Here is the content of the description '
                   'file including your new experiment.')
        log.info(df_exp_descr_new)

        answ_chg = input('Is the new file right ? (y/n/abort).\n'
                         'If you type n, you will be able to change '
                         'column values\n'
                         'If you type abort, the process of adding '
                         'the experiment {} to the reference is stoped.\n'
                         '(y/n/abort) : '
                         ''.format(exp))
        if answ_chg.upper() == 'Y':
            # save new file
            df_exp_descr_new.to_csv(f_exp_descr,sep=';',index=False)

            # get out of the loop
            return False

        elif answ_chg.upper() == 'N':
            answ_col = input('Which column field you want to change ?')

            if answ_col in df_exp_descr.keys():
                dict_line[answ_col] = input('{} : '.format(answ_col))
            else:
                log.warning('{} not in columns!'.format(answ_col))
                log.info('Columns are {}\n'.format(list(df_exp_descr.columns)))

        elif answ_chg.upper() == 'ABORT':
            exit()

    return()


def main(exp,
         tests,
         p_stages=paths.p_stages,
         p_ref_csv_files=paths.p_ref_csv_files,
         ltestsuite=False,
         lverbose=False):

    # initialisation
    new_branch_name = 'test_add_{}'.format(exp)
    files_to_commit = []

    # fill up file 'Exps_description.csv' with additional 
    # information via user input
    f_exp_descr = os.path.join(p_ref_csv_files,'Exps_description.csv')
    if not ltestsuite:
        add_line_descr_f(exp=exp,f_exp_descr=f_exp_descr)
    files_to_commit.append(f_exp_descr)

    for test in tests:
        test_cfg = get_config_of_current_test(test)

        csv_file = utils.clean_path(p_stages,
                                    'test_postproc_{}_{}.csv'
                                    .format(test,exp))

        # what is the filename in the reference pool
        filename_in_ref_dir = '{}_{}.csv'.format(test_cfg.ref_name,exp)
        # what is the location to store that file
        place_for_reference = os.path.join(p_ref_csv_files,
                                           test,
                                           filename_in_ref_dir)

        log.debug('Copy {} to {}'.format(csv_file,place_for_reference))

        if not ltestsuite:
            shutil.copy(csv_file,place_for_reference)

        files_to_commit.append(place_for_reference)

        # copy pdf with bar-plots from Welch's-test
        if test == 'welch':

            pdf_file = utils.clean_path(p_stages,
                                        '{}_{}.pdf'.format(test_cfg.ref_name,
                                                           exp))

            # what is the name of the pdf in the reference pool
            filename_in_ref_dir = '{}_plots.pdf'.format(test_cfg.ref_name)
            # what is the location to store that file
            place_for_reference = os.path.join(p_ref_csv_files,
                                               test,
                                               filename_in_ref_dir)

            log.debug('Copy {} to {}'.format(csv_file,place_for_reference))
            files_to_commit.append(place_for_reference)

            if not ltestsuite:
                shutil.copy(pdf_file,place_for_reference)

    # root is important to not fail during git commands
    os.chdir(paths.rootdir)

    # checkout new branch
    if not ltestsuite:
        log.info('Create and checkout new branch {}'.format(new_branch_name))
        git_cmd = 'git checkout -B {}'.format(new_branch_name)
        utils.shell_cmd(git_cmd,py_routine='add_exp_to_ref.py')

        # commit all modified files prior in the function to git
        for file in files_to_commit:
            git_cmd = 'git add {}'.format(file)
            log.debug(git_cmd)
            utils.shell_cmd(git_cmd, py_routine=__name__)

        log.debug('Commit files {}'.format(files_to_commit))
        commit_message = input('Please type your commit message :')
        git_cmd = 'git commit -m "{}"'.format(commit_message)
        utils.shell_cmd(git_cmd, py_routine=__name__)

    # Finish
    log.info(Style.GREEN('Files are added in the new branch: '
                         '{} in your local git repository.'
                         .format(new_branch_name)))
    log.info('To add the file to the official repository, '
             'please perform the following steps:')
    log.info('1. Push the new branch into the official repo:')
    log.info('   git push --set-upstream origin {}'.format(new_branch_name))
    log.info('2. On the Open Web interface (GitHub) , open a Pull Request.')

    log.banner('End add_exp_to_ref for experiment {}'.format(exp))
    return()


if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--exp','-e', dest='exp',
                        required=True,
                        help='exp to add')

    parser.add_argument('--p_stages', dest='p_stages',
                        default=paths.p_stages,
                        help='relative or absolute path of the csv \
                                files of the testresults')

    parser.add_argument('--p_ref_csv_files', dest='p_ref_csv_files',
                        default=paths.p_ref_csv_files,
                        help='path to the pool of csv files, \
                            one per reference experiment')

    parser.add_argument('--tests','-t', dest='tests',
                        default=['welch','fldcor','rmse','emi'],
                        nargs='+',
                        help='Tests to add to reference pool')

    parser.add_argument('--verbose','-v', dest='lverbose',
                        action='store_true',
                        help='Debug output')

    parser.add_argument('--testsuite','-ts', dest='ltestsuite',
                        action='store_true',
                        help='Run of testsuite')

    args = parser.parse_args()

    # init logger
    logger_config.init_logger(args.lverbose,__file__)

    log.banner('Start execute {} as main()'.format(__file__))

    # make all paths from user to absolute paths
    args.p_stages = utils.abs_path(args.p_stages)
    args.p_ref_csv_files = utils.abs_path(args.p_ref_csv_files)

    main(exp=args.exp,
         tests=args.tests,
         p_stages=args.p_stages,
         p_ref_csv_files=args.p_ref_csv_files,
         ltestsuite=args.ltestsuite,
         lverbose=args.lverbose)

    log.banner('End execute {} as main()'.format(__file__))

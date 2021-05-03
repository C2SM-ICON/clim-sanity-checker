# standard modules
import argparse
import os
import glob
import shutil
import sys
from scipy import stats

# aliased standard modules
import pandas as pd
import numpy as np

# modules of sanity checker
import add_exp_to_ref
import lib.paths as paths
import lib.utils as utils
import perform_test
import process_data
import lib.logger_config as logger_config

# standalone imports
from lib.logger_config import log
from lib.color import Style
from lib.test_config import get_config_of_current_test

'''
Module providing functions to perform the test. It contains:

    - generate_first_ref: create the first reference for test "welch" and "emi"

    - add_color_df_result: Add the color for the graph
            to the dataframe with the test results         

    - print_warning_color: Print dataframe with the color indicated in col_warn

    - sort_level_metric: sort results according to metric level,
            bin results into significance classes from metric_levels

    - pattern_correlation: perform pattern correlation test

    - rmse: perform RMSE test

    - welch_test: perform Welch's t-test using "stats.ttest_ind"

    - emissions: perform emission test

    - create_big_df: Create big dataframe form list of csv files

    -main: controls all function in this module, can be called as main()

            Help: python perform_test.py --help

C.Siegenthaler 07.2020 (C2SM)
J.Jucker 01.2021 (C2SM)

'''

def generate_first_ref(exp, test, test_cfg, p_ref_csv_files,p_stages):

    target_ref_directory = os.path.join(p_ref_csv_files,test)
    os.makedirs(target_ref_directory,exist_ok=True)

    first_ref_data = os.path.join(p_stages,
                                  'test_postproc_{}_{}.csv'.format(test,
                                                                   exp))

    first_ref_filename = '{}_{}.csv'.format(test_cfg.ref_name,exp)

    place_for_first_reference = os.path.join(target_ref_directory,
                                             first_ref_filename)

    shutil.copy(first_ref_data,place_for_first_reference)

    log.banner('')
    log.banner('First reference created: {}'.format(first_ref_filename))
    log.banner('')

    log.info(Style.ORANGE('You have two possibilities now: \n'
                          ' \n'
                          '1: Restart clim-sanity-checker '
                          'with another experiment \n'
                          ' \n'
                          '2: Commit and push the reference in {} ' 
                          'to Git \n' 
                          .format(utils.rel_path(place_for_first_reference))))

    sys.exit(0)


def add_color_df_result(df_result,metric_thresholds):

    df_result['col-graph'] = np.nan
    for metric_lev in metric_thresholds:
        df_result.loc[df_result.level == metric_lev.level,'col-graph'] = \
            metric_lev.col_graph

    return df_result


def print_warning_color(df_result, metric_thresholds, metric):

    # dataframe containing only variables a warning has to be printed
    df_warning = df_result[df_result['level'] != 'high']

    log.info('-------------------------------------------'
             '-------------------------------------------'
             '--------------------')

    if df_warning.size > 0:

        log.warning('The following variables give problematic '
                    '{} : \n'.format(metric))

        # for each level of warning, print the dataframe
        for metric_lev in metric_thresholds:
            if metric_lev != 'high':

                # dataframe containing only this level of warning
                df_print_warn = df_warning[
                    df_warning.level == metric_lev.level]

                # print
                if df_print_warn.size > 0:
                    log.info('Confidence is {} for {} '
                             .format(metric_lev.level.upper(),metric))
                    log.info(metric_lev.col_txt(df_print_warn))
    else:
        log.info(
            Style.GREEN(
                'The experiment is fine. ' 
                'No {} under {} \n').format(metric,
                                            metric_thresholds[1].p_thresh))

    log.info('-------------------------------------------'
             '-------------------------------------------'
             '--------------------')

    return

def sort_level_metric(df_result, metric_thresholds, metric):

    # define out the level of Warning
    bins = [t.p_thresh for t in metric_thresholds]

    bins = [-1e-10] + bins

    metric_levels = [t.level for t in metric_thresholds]

    # sort each variable into bins in function of its p-values
    df_result['level'] = pd.cut(df_result[metric], bins, labels=metric_levels)

    return df_result


def pattern_correlation(df_exp,test_cfg):
    '''
    Perform pattern correlation test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :return: result of the pattern correlation in a dataframe
    '''

    row_list_df = []

    for var in df_exp.keys():
        if 'exp' in var:
            continue
        log.debug("Pattern correlation test for {}".format(var))

        # append results for construction datframe df_result
        dict1 = {'variable': var, test_cfg.metric: df_exp[var].iloc[0]}
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, 
                             columns=['variable',
                                      test_cfg.metric])

    df_result.sort_values(by=[test_cfg.metric], inplace=True)

    return (df_result)


def rmse(df_exp,test_cfg):
    '''
    Perform rmse  test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :return: result of the pattern correlation in a dataframe
    '''

    row_list_df = []

    for var in df_exp.keys():
        if 'exp' in var:
            continue
        log.debug("Rmse test for {}".format(var))

        # append results for construction datframe df_result
        dict1 = {'variable': var, test_cfg.metric: df_exp[var].iloc[0]}
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, 
                             columns=['variable',
                                      test_cfg.metric])

    df_result.sort_values(by=[test_cfg.metric], inplace=True)

    return (df_result)


def welch_test(df_a, df_b, filename_student_test=''):
    '''
    Perform Welch t-test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :param filename_student_test: filename for writing result 
            of t-test result into a csv file
    :return: result of the student test in a dataframe
    '''

    row_list_df = []

    for var in df_b.keys():
        if 'exp' in var:
            continue
        log.debug("Welch's t-test for {}".format(var))
        # Welch's t-test
        t, p = stats.ttest_ind(df_a[var], 
                               df_b[var], 
                               equal_var=False, 
                               nan_policy='omit')

        # append results for construction datframe df_result
        dict1 = {'variable': var, 't-value': t, 'p-value': p}
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, 
                             columns=['variable','t-value','p-value'])

    # sort per p value
    df_result.sort_values(by=['p-value'], inplace=True)

    # if a filename is given, write the student-stest 
    # result into the file named filename_student_test
    if len(filename_student_test) > 0:
        log.info('Write result to {}'.format(filename_student_test))
        df_result.to_csv(filename_student_test, sep=',')

    return (df_result)


def emissions(df_exp, df_ref, test_cfg,filename_student_test=''):
    '''
    Perform emissions test for each variable of dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :param filename_student_test: filename for writing 
            result of t-test result into a csv file
    :return: result of the emissions test in a dataframe
    '''

    row_list_df = []

    # select base reference for emission
    df_ref = df_ref.loc[df_ref['exp'] == 'emis_base_ref']

    for var in df_exp.keys():
        if 'exp' in var:
            continue
        log.debug("Emissions test for {}".format(var))

        abs_deviation = abs(df_exp[var].iloc[0] - df_ref[var].iloc[0])
        rel_deviation = abs_deviation / df_ref[var].iloc[0] * 100

        # append results for construction datframe df_result
        dict1 = {'variable': var, test_cfg.metric: rel_deviation}
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, columns=['variable',test_cfg.metric])

    # sort per p value
    df_result.sort_values(by=[test_cfg.metric], inplace=True)

    return (df_result)


def create_big_df(ref_names, list_csv_files, filename_csv=''):
    '''
    :param list_csv_files: list of csv files for the big dataframe
    :return: big dataframe containing the whole data
    '''

    # initialise big empty dataframe
    df_tot = pd.DataFrame()

    # create big dataframe
    for fexp in list_csv_files:

        exp = os.path.basename(fexp).rstrip('.csv').replace('glob_means_','')

        # read the csv file
        if os.path.isfile(fexp):
            df_exp = pd.read_csv(fexp, sep=';')
            df_exp['exp'] = exp

            # append dataframe of exp to the total dataframe
            df_tot = df_tot.append(df_exp, sort=False)

        else:
            log.warning('csv file is not a file : {}'.format(fexp))

    if len(filename_csv) > 0:
        df_tot.to_csv(filename_csv, sep=';')

    return df_tot


def main(new_exp,
         results_data_processing,
         tests,
         p_stages,
         p_ref_csv_files,
         ltestsuite,
         f_vars_to_extract):

    df_exp = {}
    df_ref = {}
    p_csv_files = {} 
    testresult_csv = {}
    df_result = {}

    for test in tests:

        test_cfg = get_config_of_current_test(test)

        if test == 'welch' or test == 'emi':

            log.info('Prepare references for test {}'.format(test))

            results_data_processing[test]['exp'] = new_exp

            # list of paths to all csv files
            p_csv_files[test] = glob.glob(
                os.path.join(p_ref_csv_files,
                             test,'{}_*csv'.format(test_cfg.ref_name)))
            if len(p_csv_files[test]) == 0:
                log.warning('No reference files '
                            'found in {}'.format(p_ref_csv_files))

                generate_first_ref(new_exp, 
                                   test, 
                                   test_cfg, 
                                   p_ref_csv_files, 
                                   p_stages)

            log.debug('{} reference(s) found for test \
                      {}'.format(len(p_csv_files[test]),test))

            # create big dataframe containing all reference exps
            df_ref[test] = create_big_df(test_cfg.ref_name,
                                         list_csv_files=p_csv_files[test])

            # Exclude all the non-desired variables (1) var from file, 2) exp)
            full_p_f_vars = os.path.join(paths.p_f_vars_proc,test,
                                         f_vars_to_extract)
            vars_to_analyse = list(pd.read_csv(full_p_f_vars, sep=',')
                                   ['var'].values)
            vars_to_analyse.append('exp')
            try:
                df_ref[test] = df_ref[test][vars_to_analyse]
            except KeyError as e:
                log.warning(e)
                log.error('Variables defined in {} are \
                          not contained in reference \
                          {}'.format(utils.rel_path(f_vars_to_extract),
                                     utils.rel_path(p_ref_csv_files)))

            df_exp[test] = results_data_processing[test][vars_to_analyse]

            log.info('References for test {} prepared'.format(test))

            testresult_csv[test] = os.path.join(
                p_stages,
                'result_{}_{}.csv'.format(test,
                                          new_exp))
        else:
            df_exp[test] = {}

        if test == 'welch':
            log.banner('')
            log.banner("Perform Welch's t-test for each variable")
            log.banner('')
            df_result[test] = welch_test(
                df_a=df_ref[test], 
                df_b=df_exp[test],
                filename_student_test=testresult_csv[test])
            df_result[test]['p-value [%]'] = df_result[test]['p-value'] * 100.

        if test == 'fldcor':
            log.banner('')
            log.banner("Perform fldcor test for each variable")
            log.banner('')
            df_result[test] = pattern_correlation(df_exp[test],test_cfg)

        if test == 'emi':
            log.banner('')
            log.banner("Perform emission test for each variable")
            log.banner('')
            df_result[test] = emissions(df_exp[test], df_ref[test],test_cfg)

        if test == 'rmse':
            log.banner('')
            log.banner("Perform rmse test for each variable")
            log.banner('')
            df_result[test] = rmse(df_exp[test], test_cfg)

        df_result[test] = sort_level_metric(df_result[test],
                                            test_cfg.metric_threshold,
                                            test_cfg.metric)
        df_result[test] = add_color_df_result(df_result[test],
                                              test_cfg.metric_threshold)

        print_warning_color(df_result[test],
                            test_cfg.metric_threshold,
                            test_cfg.metric)

        if ltestsuite:
            for test in tests:
                test_cfg = get_config_of_current_test(test)
                utils.exit_if_testresult_is_bad(test,
                                                df_result[test], 
                                                test_cfg.metric_threshold,
                                                test_cfg.metric)

    return df_result,df_ref


if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--exp','-e', dest='exp',
                        required=True,
                        default='euler_REF_10y',
                        help='exp to proceed')

    parser.add_argument('--p_stages', dest='p_stages',
                        default=paths.p_stages,
                        help='relative or absolute path \
                             to write csv files of the testresults')

    parser.add_argument('--wrkdir','-w', dest='wrk_dir',
                        default=paths.p_wrkdir,
                        help='relative or absolute path to working directory')

    parser.add_argument('--p_ref_csv_files', dest='p_ref_csv_files',
                        default=paths.p_ref_csv_files,
                        help='relative or absolute path to reference files')

    parser.add_argument('--f_vars_to_extract', dest='f_vars_to_extract',
                        default='vars_echam-hammoz.csv',
                        help='File containing variables to anaylse')

    parser.add_argument('--verbose','-v', dest='lverbose',
                        action='store_true',
                        help='Debug output')

    parser.add_argument('--tests','-t', dest='tests',
                        default=['welch','fldcor','rmse','emi'],
                        nargs='+',
                        help='Tests to apply on your data')

    parser.add_argument('--testsuite','-ts', dest='ltestsuite',
                        action='store_true',
                        help='Run of testsuite')

    args = parser.parse_args()

    logger_config.init_logger(args.lverbose,__file__)

    log.banner('Start execute {} as main()'.format(__file__))

    args.wrk_dir = utils.abs_path(args.wrk_dir)
    args.p_stages = utils.abs_path(args.p_stages)
    args.p_ref_csv_files = utils.abs_path(args.p_ref_csv_files)

    os.chdir((args.wrk_dir))
    log.info('Current directory is {}'.format(args.wrk_dir))

    log.info('Read processed data from csv for...')
    results_data_processing = {}
    for test in args.tests:
        log.info('{}'.format(test))
        f_csv = utils.clean_path(
            args.p_stages, 'test_postproc_{}_{}.csv'.format(test,
                                                            args.exp))
        results_data_processing[test] = pd.read_csv(f_csv, sep=';')
    log.info('...done') 

    main(new_exp=args.exp,
         results_data_processing=results_data_processing,
         p_stages=args.p_stages,
         p_ref_csv_files=args.p_ref_csv_files,
         f_vars_to_extract=args.f_vars_to_extract,
         ltestsuite=args.ltestsuite,
         tests=args.tests)

    log.banner('End execute {} as main()'.format(__file__))

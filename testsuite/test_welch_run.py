import shutil
import testsuite.utils as utils


def test_welch_first_ref():
    input_dir = 'testsuite/data'
    exp_name = 'first-ref'

    files_generated = utils.generate_data(input_dir,
                                          exp_name,
                                          '2d_A',
                                          'TSURF')

    files_generated.extend(utils.generate_data(input_dir,
                                               exp_name,
                                               '2d_B',
                                               'T2M'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'

    ref_dir = 'testsuite/first_ref'
    shutil.rmtree(ref_dir, ignore_errors=True)

    cmd = 'python sanity_test.py -e {} -t welch --spinup 0 \
            --p_stages testsuite/stages \
            --wrkdir testsuite/workdir \
            --p_ref_csv_files {} --f_vars_to_extract \
            vars_welchs_test.csv -c -ts'.format(exp_name, ref_dir)

    status, _ = utils.shell_cmd(cmd)

    utils.delete_data(files_generated)
    assert status == 0, 'sanity_test.py failed'


def test_welch_embed():
    input_dir = 'testsuite/data'
    exp_name = 'run_embed'

    files_generated = utils.generate_data(input_dir,
                                          exp_name,
                                          '2d_A',
                                          'TSURF')

    files_generated.extend(utils.generate_data(input_dir,
                                               exp_name,
                                               '2d_B',
                                               'T2M'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'

    cmd = 'python sanity_test.py -e {} -t welch --spinup 0 \
            --p_stages testsuite/stages \
            --wrkdir testsuite/workdir \
            --p_ref_csv_files testsuite/ref --f_vars_to_extract \
            vars_welchs_test.csv -c -ts'.format(exp_name)

    status, _ = utils.shell_cmd(cmd)

    utils.delete_data(files_generated)
    assert status == 0, 'sanity_test.py failed'


def test_welch_chained():
    input_dir = 'testsuite/data'
    exp_name = 'run_chained'

    files_generated = utils.generate_data(input_dir,
                                          exp_name,
                                          '2d_A',
                                          'TSURF')

    files_generated.extend(utils.generate_data(input_dir,
                                               exp_name,
                                               '2d_B',
                                               'T2M'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'

    cmd = 'python process_data.py -e {} -t welch --spinup 0 \
            --p_stages testsuite/stages \
            --wrkdir testsuite/workdir \
            --f_vars_to_extract vars_welchs_test.csv \
            -c'.format(exp_name)

    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'process_data.py failed'

    cmd = 'python perform_test.py  -e {} -t welch  \
            --p_stages testsuite/stages \
            --wrkdir testsuite/workdir \
            --p_ref_csv_files testsuite/ref --f_vars_to_extract \
            vars_welchs_test.csv -ts'.format(exp_name)

    status, _ = utils.shell_cmd(cmd)

    utils.delete_data(files_generated)

    assert status == 0, 'perform_test.py failed'

# Sanity Checker for climate model 

This tool allows to statistically check the output of a new climate simulation against a set of reference simulations, 
in order to identify systematic bias in the climatological results (due for example to a bug, or too aggressive compiler options). 

This tool is based on a excel tool David Neubaurer (ETHZ) developed for ECHAM-HAMMOZ : 
https://redmine.hammoz.ethz.ch/projects/hammoz/wiki/Reference_experiments_to_test_computing_platform 

It allows to analyze annual global means of a 10 year period (any other period of time is possible as well) for ECHAM-HAMMOZ and ICON.
In general data from other models can be processed as well.

Currently there are 3 different tests available:
   * Welch's t-Test
   * Pattern Correlation Test
   * Emissions Test (I/O)
   
   For more details about the implementation of each test see [test descriptions](tests.md).
  
## Structure

This tool consists of three modules that can be run independently and a wrapper to execute them one after each other:

   * [sanity_test.py](sanity_test.py), wrapper that chains modules below
   * [process_data.py](process_data.py), convert raw model output into pd.dataframe
   * [perform_test.py](perform_test.py), apply test based on the pd.dataframe and references stored in [references](ref)
   * [add_exp_to_ref.py](add_exp_to_ref.py), add .csv with results of tests to [references](ref)
  
Each module writes intermediate files to a directory passed with argument --p_stages, the subsequent module then looks into
that directory for files needed. The tool is written in a way, that no time-consuming processing step is done twice.

Detailed information about the structure of the clim-sanity-checker can be found in [structure](structure.md).

## Quick start

**Configure paths with paths_init.py:**  
*python paths_init.py -pr /project/s903/nedavid/plattform_comparison/*

This will create the file *paths.py* in the folder [lib](lib) for later use. Note that any path defined in *paths.py*
can be overridden by command-line arguments.

**Run sanity_test.py:**  
*python sanity_test.py -exp your_experiment_name --f_vars_to_extract vars_echam-hammoz.csv --raw_f_subfold Raw*

This command will launch:
   * The preprocessing for the model output (stored in the folder *Raw*) based on the *vars_echam-hammoz.csv* variable definitions.
   * Perform all tests.
   * Asks you, whether this test should be added to the reference pool or not.
   
 Detailed information about all available options of *sanity_test.py* or other modules is provided in [module arguments](module_arguments.md).
 
 ## Variable Definition
 
 This tool can analyze all possible variables or combinations of individual fields. One needs to define
 the variable name, the formula to derive it from model output and the file-extension (e.g. atm_2d) for each test
 in [variables_to_process](variables_to_process). An example for ECHAM-HAMMOZ is [vars_echam-hammoz.csv](variables_to_process/welchstest/vars_echam-hammoz.csv).
 
 For ECHAM-HAMMOZ and ICON there exist already such a table for some of the test:
 
 #### ECHAM-HAMMOZ
The variable definitons for the Welch's t-Test are derived from the publication of
*Neubauer et al.: The global aerosol–climate model ECHAM6.3–HAM2.3 – Part 2: Cloud evaluation, aerosol radiative forcing, and climate sensitivity, Geosci. Model Dev., 12, 3609–3639, https://doi.org/10.5194/gmd-12-3609-2019, 2019*.  
For the Emission Test the variable definitions are taken from an excel-sheet provided by David Neubauer.

#### ICON
The variable definitions for the Welch's t-Test are adapted from the file below provided by Colin Tully:  
![vars_icon](https://user-images.githubusercontent.com/39263956/103921491-dfbe8b80-5112-11eb-8ee7-abc19ac3ce2d.png)

## Missing
1. analyse of variables only over ocean

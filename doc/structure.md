# Module description
All important processing steps for each of the three modules are described below. Only steps relevant to data processing are described.

## process_data.py

#### standard_postproc
Computes the variables defined in file 
f_vars_to_extract from the raw netcdf model output files using the CDO library.
For the raw model output, all the files located in [p_raw_files]/[exp]/[raw_f_subfold] 
minus the spinup (default = 3 files) are used.

The file f_vars_to_extract 
contains the definitions of the variables which are computed. 
The expected file is an array with 3 columns separated by ',':
- 1st column : variable name in the output files
- 2nd column : formula to compute this variable, based on native model variable name
- 3rd column : raw output stream name where the native model variable names of the 2nd column can be found. 

Files with a problem are skipped. All variables are then merged into one single netCDF-file that is stored in
the directory passed as argument *--p_stages*

The function in combination with timeser_proc_nc_to_df has been based on the script general_proc.sh written by 
Sylvaine Ferrachat (IAC, ETHZ).

**CAUTION:**  
For the ECHAM-data stored in /project/s903/nedavid/platform a hack is introduced, because for some experiments no unprocessed model output
is available. In case no raw data is found, the module looks for other directories, containing processed timeseries of the data. If some files are found, the user 
has the possibility to choose via input what file to choose.
This piece of code is poorly implemented and can easily fail if applied to other use-cases!


#### timeser_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get a timeseries of annual mean values for each field.
Finally a .csv file of this timeseries is stored (this file serves as a reference if the experiment is added to the reference pool).

#### pattern_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get multi-annual means per gridcell for each field.
Then the actual field-correlation using CDO is computed. The resulting R^2-values for each field is stored in a .csv file for later use.
This .csv file serves as described above as a reference if the experiment is added to the reference pool.

#### emis_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get a mean value over the entire period for each field.
This .csv file serves as described above as a reference if the experiment is added to the reference pool.

#### rmse_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get multi-annual means per gridcell for each field.
In a second step, both the reference and the model output is normalized using mean and standard-deviation for each field. These two normalized
2D-NetCDF are then used to compute the root mean square error.


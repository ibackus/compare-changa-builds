# -*- coding: utf-8 -*-
"""
This example generates test run-param files for some dustydisk tests.  These
run-param files can then be used by runTest.runTest to run the tests.

The user should definitely read through this script and the script
setup_dustydisk_params.py that it calls to generate params for the tests.

Param files are saved as .json files in the simulation run directory.

The steps/results for this test are:
    
    1.  Set-up simulation directories for several tests/several ChaNGa 
        installations (setup_dustydisk_params.py)
        i.  We have what I call a 'control' version of ChaNGa and a 'test'
            version to test against.
        ii. For both versions, we create simulation folders for all tests to
            run under results/
    2.  Compile ChaNGa for the different tests.  The tests in general can 
        use different compilation flags.  Binaries are copied to the simulation
        directories.
    3.  Run the tests with ChaNGa.  There are several available runtime
        .param files available (in the test directory) which the user can
        choose in setup_dustydisk_params.py
    4.  Analyze the tests by comparing results of the 'test' and 'control'
        versions of ChaNGa.  (see compchanga.compare in compchanga/compare.py)

Created on Tue Oct  4 13:23:16 2016

@author: ibackus
"""
from compchanga import runbuild, compare

# Run script to generate param files.  this script generates paramfiles which
# is a list of run-time param files used by the test utilities for running
# and compiling tests
execfile('setup_dustydisk_params.py')
print 'Run param files:', paramfiles
print 'Control sim directories:', controlSims
print 'Test sim directories:', testSims

# -------------------------
# NOTE
# The flag 'newonly' will only run things which have not finished already.
# this is useful for re-running after crashing
#
# You can overwrite directory contents by setting newonly=False
#--------------------------
# Build ChaNGa for the tests  (changa binary will be copied to simulation dirs)
success = runbuild.buildChanga(paramfiles, newonly=True, require_success=True)
# Run the generated tests (contained in paramfiles)
# Several can be run in parallel by specifying the number of jobs to spawn
# with proc
success = runbuild.runManyTests(paramfiles, newonly=True, proc=4, require_success=False)

# Now analyze tests (looking at the first 2 simulation directories)
print 'ANALYZING tests:'
results = []
for controlSim, testSim in zip(controlSims, testSims):
    # compare the results in the controlSim directory to those in testSim
    print '\n\n COMPARING TEST'
    print 'control:', controlSim
    print 'test:', testSim
    results.append(compare.compareDustyDisk([testSim, controlSim]))

# -*- coding: utf-8 -*-
"""


Created on Tue Oct  4 13:23:16 2016

@author: ibackus
"""
from compchanga import runbuild, compare
from multiprocessing import cpu_count

# Run script to generate param files.  this script generates paramfiles which
# is a list of run-time param files used by the test utilities for running
# and compiling tests
execfile('setup_sphpressureterms_params.py')
print 'Run param files:', paramfiles
print 'Control sim directories:', controlSims
print 'Test sim directories:', testSims

# -------------------------
# NOTE
# The flag 'newonly' will only run things which have not finished already.
# this is useful for re-running after crashing
#--------------------------
# Build ChaNGa for the tests  (changa binary will be copied to simulation dirs)
success = runbuild.buildChanga(paramfiles, newonly=True, require_success=True)
# Run the generated tests (contained in paramfiles)
# Several can be run in parallel by specifying the number of jobs to spawn
# with proc
success = runbuild.runManyTests(paramfiles, newonly=True, proc=cpu_count()-1, 
                                require_success=False)

# Now analyze tests (looking at the first 2 simulation directories)
print 'ANALYZING tests:'
results = []
for controlSim, testSim in zip(controlSims, testSims):
    # compare the results in the controlSim directory to those in testSim
    print '\n\n COMPARING TEST'
    print 'control:', controlSim
    print 'test:', testSim
    results.append(compare.compareAgora([controlSim, testSim]))
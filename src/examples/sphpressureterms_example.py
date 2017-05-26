# -*- coding: utf-8 -*-
"""
This script will perform and analyze a suite of tests intended to validate
the sphpressureterms refactor.  This will compare the results of two versions
of ChaNGa (contained in different folders) for several tests using multiple
compile-time options in order to determine if everything is functioning
as it should.

If anything fails along the way, you can re-run this script and it should try
to only complete unfinished steps.  This behavior can be changed by setting
overwrite=True in setup_sphpressureterms_params.py or by changing the 
various newonly arguments to newonly = False.

STEP 1
The first step is to set-up the test-runs.  this is handled by executing
the script setup_sphpressureterms_params.py

STEP 2 
The second step is to compile ChaNGa for each test.  The various tests
all use different compile time flags.  ChaNGa binaries will be stored in the
simulation folders.  This will use a custom built ChaNGa configure script
with extra command-line options to allow more fine-tuning of build-time flags.
The script is located in userconfig/sphpressureterms/ (from the base of the
repo) and may need to be updated by hand if the public or sphpressureterms3
branches are modified.

STEP 3
The third step is to analyze the results.  This is handled by 
compare.compareTests(...).  Analysis just compares the results of the 'control'
run and the 'test' run.  This step is verbose.  A summary of test results
will be at the end.  The goal is to have VERY small mean fractional errors,
i.e. of order double precision (like 1e-16).  for some values, larger is ok.

Created on Tue Oct  4 13:23:16 2016

@author: ibackus
"""
import compchanga
from compchanga import runbuild, compare
from multiprocessing import cpu_count

# Run script to generate param files.  this script generates paramfiles which
# is a list of run-time param files used by the test utilities for running
# and compiling tests
execfile('setup_sphpressureterms_params.py')
print 'Run param files:', paramfiles
print 'Control sim directories:', controlSims
print 'Test sim directories:', testSims
print 'test names:', testNames

# -------------------------
# NOTE
# The flag 'newonly' will only run things which have not finished already.
# this is useful for re-running after crashing
#--------------------------
# Build ChaNGa for the tests  (changa binary will be copied to simulation dirs)
success = False
success = runbuild.buildChanga(paramfiles, newonly=True, require_success=True)
# Run the generated tests (contained in paramfiles)
# Several can be run in parallel by specifying the number of jobs to spawn
# with proc
if success:
    success = runbuild.runManyTests(paramfiles, newonly=True, proc=cpu_count()-1, 
                                    require_success=False)

if success:
    # Initialize results containers
    results = {}
    params = {}
    for testName in compchanga.config.tests:
        results[testName] = []
        params[testName] = []
    # ------------------------------------------
    # Now analyze tests (looking at the first 2 simulation directories)
    # ------------------------------------------
    print '\n--------------------------------------'
    print 'FULL ANALYSIS'
    for controlSim, testSim, testName, paramfile in \
    zip(controlSims, testSims, testNames, paramfiles):
        # compare the results in the controlSim directory to those in testSim
        print '\n\n COMPARING TEST'
        print 'test name:', testName
        print 'control:', controlSim
        print 'test:', testSim
        # keep track of run params
        par= compchanga.runTest.loadRunParam(paramfile)
        params[testName].append(par)
        # Run the analysis
        result = compare.compareTests([controlSim, testSim], testName)
        results[testName].append(result)
    
    # ------------------------------------------
    # Summarize results
    # ------------------------------------------
    print '\n--------------------------------------'
    print 'SHOCKTUBE SUMMARY'
    testName = 'shocktube'
    parlist = params[testName]
    resultlist = results[testName]
    for i, (par, result) in enumerate(zip(parlist, resultlist)):
        print ''
        print '** Test {} **'.format(i)
        print 'configure options:', par['configOpts']
        compare.summarizeResults(result, testName)
    
    print '\n--------------------------------------'
    print 'SEDOV BLAST SUMMARY'
    testName = 'sedov'
    parlist = params[testName]
    resultlist = results[testName]
    for i, (par, result) in enumerate(zip(parlist, resultlist)):
        print ''
        print '** Test {} **'.format(i)
        print 'configure options:', par['configOpts']
        compare.summarizeResults(result, testName)
    
    print '\n--------------------------------------'
    print 'AGORA SUMMARY'
    testName = 'agora-short'
    parlist = params[testName]
    resultlist = results[testName]
    for i, (par, result) in enumerate(zip(parlist, resultlist)):
        print ''
        print '** Test {} **'.format(i)
        print 'configure options:', par['configOpts']
        compare.summarizeResults(result, testName)
    
    
    print '\n--------------------------------------'
    print 'COLLAPSE SUMMARY'
    testName = 'collapse'
    parlist = params[testName]
    resultlist = results[testName]
    for i, (par, result) in enumerate(zip(parlist, resultlist)):
        print ''
        print '** Test {} **'.format(i)
        print 'configure options:', par['configOpts']
        compare.summarizeResults(result, testName)
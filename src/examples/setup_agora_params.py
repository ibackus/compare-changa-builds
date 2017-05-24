# -*- coding: utf-8 -*-
"""
NOTE: the compchanga directory (package directory) must be added to the 
PYTHONPATH in order for this to work.

This example generates test run-param files for some agora tests.  These
run-param files can then be used by runTest.runTest to run the tests.

see also agora_test_example.py

Created on Tue Oct  4 13:23:16 2016

@author: ibackus
"""
from compchanga import runTest
from compchanga.runTest import newTestConfig

# ----------------------------------------------------------------
# Optional settings
# ----------------------------------------------------------------
# overwrite param files?  This will also make the simulation appear incomplete
overwrite = False
# I want to supply my own configure script to ChaNGa to enable extra configure
# parameters
userconfigdir = '../userconfig/sphpressureterms/'
# Use a different runner (mpirun, charmrun, etc...)?
runner = None
logsavename = 'agora-short.log'
# For charmrun. default nproc is None
nproc = 1
# extra args for changa
changa_args = '-p 1'
# ----------------------------------------------------------------
# Required settings
# ----------------------------------------------------------------
# Base directory to save tests to.
# I have two versions of ChaNGa I want to compare, one I call the 'control'
# (which I think should be working right) and the other I call the 'test'
# Simulations will be saved in sub-directories of these folders
controlBaseDir = 'results/temp/control'
testBaseDir = 'results/temp/test'
# Directories containing ChaNGa to run, in this case the 'test' and 'control'
# copies of ChaNGa
changaControlDir = '/usr/lusers/ibackus/scratch/changa_uw'
changaTestDir = '/usr/lusers/ibackus/scratch/changa_uw2'
# Define tests to run (on each of these versions)
# This will run the agora-short test with different command line configure
# options and will save it with the default testName
tests = [
    newTestConfig('agora-short', '--enable-cooling=cosmo', testName=None),
    newTestConfig('agora-short', '--enable-cooling=cosmo --enable-rtforce=no', testName=None)
]

# ----------------------------------------------------------------
# Set-up the test param files
# ----------------------------------------------------------------
paramfiles = []
controlSims = []
testSims = []
# Run the control simulations
for test in tests:        
    args, paramfile, simdir = runTest.makeparam(controlBaseDir, changaControlDir, 
        test, overwrite, nproc, changa_args, runner=runner, userconfigdir=userconfigdir)
    paramfiles.append(paramfile)
    controlSims.append(simdir)
# Run the 'test' simulations
for test in tests:        
    args, paramfile, simdir = runTest.makeparam(testBaseDir, changaTestDir, 
        test, overwrite, nproc, changa_args, runner=runner,userconfigdir=userconfigdir)
    paramfiles.append(paramfile)
    testSims.append(simdir)
# Save a list of paramfiles (this can be used later to run the tests)
runTest.saveParamList(paramfiles, logsavename)

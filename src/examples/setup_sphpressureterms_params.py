# -*- coding: utf-8 -*-
"""
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
logsavename = 'sphpressureterms.log'
# For charmrun. default nproc is None
nproc = 1
# extra args for changa
changa_args = ''
# Verbosity (not 100% implemented really)
verbose = True
# ----------------------------------------------------------------
# Required settings
# ----------------------------------------------------------------
# Base directory to save tests to.
# I have two versions of ChaNGa I want to compare, one I call the 'control'
# (which I think should be working right) and the other I call the 'test'
# Simulations will be saved in sub-directories of these folders
controlBaseDir = 'results/sphpressureterms/control'
testBaseDir = 'results/sphpressureterms/test'
# Directories containing ChaNGa to run, in this case the 'test' and 'control'
# copies of ChaNGa.  To make this simple, I've got two copies of the git
# repo on my machine
changaControlDir = '/usr/lusers/ibackus/scratch/changa_uw2/changa_uw2'
changaTestDir = '/usr/lusers/ibackus/scratch/changa_uw'
# Initialize tests to run (on each of these versions)
# This will run the agora-short test with different command line configure
# options and will save it with the default testName
tests = [
    # Agora tests
    newTestConfig('agora-short', '--enable-cooling=cosmo '\
                                 '--enable-diffharmonic=yes '\
                                 '--enable-feedbackdifflimit=no '),
    newTestConfig('agora-short', '--enable-cooling=cosmo '\
                                 '--enable-diffharmonic=no '\
                                 '--enable-feedbackdifflimit=yes '),
    newTestConfig('agora-short', '--enable-cooling=cosmo '\
                                 '--enable-diffharmonic=no '\
                                 '--enable-feedbackdifflimit=no '), 
    # Sedov tests
    newTestConfig('sedov', '--enable-dtadjust=yes'), 
    newTestConfig('sedov', '--enable-dtadjust=no'), 
    # Collapse tests
    newTestConfig('collapse'), 
    # Shocktube test
    newTestConfig('shocktube', '--enable-rtforce=yes'), 
    newTestConfig('shocktube', '--enable-rtforce=no')
]

# ----------------------------------------------------------------
# Set-up the test param files
# These are files that control everything about how the test will be run
# ----------------------------------------------------------------
paramfiles = []
controlSims = []
testSims = []
# Setup the control simulations
for test in tests:        
    args, paramfile, simdir = runTest.makeparam(controlBaseDir, changaControlDir, 
        test, overwrite, nproc, changa_args, runner=runner, userconfigdir=userconfigdir, 
        verbose=verbose)
    paramfiles.append(paramfile)
    controlSims.append(simdir)
# Setup the 'test' simulations
for test in tests:        
    args, paramfile, simdir = runTest.makeparam(testBaseDir, changaTestDir, 
        test, overwrite, nproc, changa_args, runner=runner,userconfigdir=userconfigdir,
        verbose=verbose)
    paramfiles.append(paramfile)
    testSims.append(simdir)
# Save a list of paramfiles (this can be used later to run the tests)
runTest.saveParamList(paramfiles, logsavename)

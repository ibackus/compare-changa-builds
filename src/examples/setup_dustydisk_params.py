# -*- coding: utf-8 -*-
"""
This test requires the disky python package, available at 
https://github.com/ibackus/diskpy

NOTE: the compchanga directory (package directory) must be added to the 
PYTHONPATH in order for this to work.

This example generates test run-param files for some dustydisk tests.  These
run-param files can then be used by runTest.runTest to run the tests.

Created on Tue Oct  4 13:23:16 2016

@author: ibackus
"""
from compchanga import runTest
from compchanga.runTest import newTestConfig

import diskpy

# ----------------------------------------------------------------
# Optional settings
# ----------------------------------------------------------------
# overwrite param files?  This will also make the simulation appear incomplete,
# meaning EACH time you run this script, re-running the tests will run them
# all from scratch
overwrite = False
# If I want to supply my own configure script to ChaNGa to enable extra configure
# parameters
#userconfigdir = '../userconfig/sphpressureterms/'
userconfigdir = None
# Use a different runner (mpirun, charmrun, etc...)?
runner = None
logsavename = 'dustydisk.log'
# For charmrun. default nproc is None
nproc = 1
# extra args for changa
changa_args = '-n 1'
# Verbosity (not 100% implemented really)
verbose = True
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
changaControlDir = '/home/ibackus/ChaNGa/changa_uw-copy/changa'
changaTestDir = '/home/ibackus/ChaNGa/changa_uw/changa'
# Define tests to run (on each of these versions)
# NOTE: grainsize and graindensity are extra parameters that I use here to
# see which build versions can have the ChaNGa runtime params of grainsize/density
controlTests = [
    newTestConfig('dustydisk', '--enable-dustygas --enable-dustgrowth',
                  paramname='graingrowth.param'),
    newTestConfig('dustydisk', '--enable-dustygas', 
        paramname='graingrowth.param'),
    newTestConfig('dustydisk', paramname='nodust.param'),
]
testTests = [
    newTestConfig('dustydisk', '--enable-dustygas=onefluid --enable-dustgrowth',
                  paramname='graingrowth.param'),
    newTestConfig('dustydisk', '--enable-dustygas=onefluid', 
        paramname='constant_grain_size.param'),
    newTestConfig('dustydisk', paramname='nodust.param'),
]

# ----------------------------------------------------------------
# Set-up the test param files
# These are files that control everything about how the test will be run
# ----------------------------------------------------------------
paramfiles = []
controlSims = []
testSims = []
# Setup the control simulations
for test in controlTests:        
    args, paramfile, simdir = runTest.makeparam(controlBaseDir, changaControlDir, 
        test, overwrite, nproc, changa_args, runner=runner, userconfigdir=userconfigdir, 
        verbose=verbose)
    paramfiles.append(paramfile)
    controlSims.append(simdir)
# Set-up the 'test' simulations
for test in testTests:        
    args, paramfile, simdir = runTest.makeparam(testBaseDir, changaTestDir, 
        test, overwrite, nproc, changa_args, runner=runner,userconfigdir=userconfigdir,
        verbose=verbose)
    paramfiles.append(paramfile)
    testSims.append(simdir)
# Save a list of paramfiles (this can be used later to run the tests)
runTest.saveParamList(paramfiles, logsavename)

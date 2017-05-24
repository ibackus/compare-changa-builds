#!/usr/bin/env python
"""
A command line utility used to run the tests in runTest.py

This one can be used to just build off of certain commits and store the
binaries in a central directory

Created on Tue Oct  4 12:01:25 2016

@author: ibackus
"""

import compare
import runTest

import numpy as np
from multiprocessing import Pool, cpu_count
import json

def buildChanga(filelist=None, filename=None, newonly=False, require_success=False):
    """
    A running utilitiy to build changa. 
    All exceptions are caught and the failure is returned
    
    NOTE: ONLY supply filelist OR filename, not both
    
    Parameters
    ----------
    filelist : list or str
        Either a list of paths to run params (i.e. the json files) OR a
        filename for a file containing a list of params.
    filename : str
        run param filename (should probably end .json)
    newonly : bool
        Don't recompile already built binaries
    
    Returns
    -------
    success : bool
        If all builds succeed, return True, else False
    """
    
    
    if (filelist is not None) and (filename is not None):
        raise ValueError, "please supply EITHER a filelist or a filename, "\
            "not both"
    if filename is not None:
        flist = [filename]
    elif filelist is not None:
        flist = filelist
        if isinstance(filelist, str):
            flist = compare.readLines(flist)
    else:
        raise ValueError, 'Must supply flist or fname'
    # Generate a list of arguments for the various builds of ChaNGa
    argDicts = compare.loadArgDicts(flist)
    # Build changa
    results = []
    for argDict in argDicts:
        if newonly:
            argDict['recompile'] = False
        try:
            result = runTest.configBuildChanga(**argDict)
        except:
            if require_success:
                raise
            result  = False
        results.append(result)

    # print a summary
    print "\nBuild success summary:"
    colwidth = 10
    for f, success in zip(flist, results):
        if success:
            string = "success".ljust(colwidth)
        else:
            string = "fail".ljust(colwidth)
        string = string + str(f)
        print string
    return np.all(results)

def runManyTests(flist, newonly=False, proc=None, require_success=False):
    """
    run the paramfiles in file flist (flist is a filename or a list of param
    files)
    
    proc can be specified to run in parallel
    """
    import compare
    import numpy as np
    if isinstance(flist, str):
        paramfiles = compare.readLines(flist)
    else:
        paramfiles = flist
    if proc is None:
        results = [runOneTest(paramfile, newonly, require_success=require_success) for paramfile in paramfiles]
    else:
        results = parallelRunTests(paramfiles, proc, newonly, require_success=require_success)
    
    # print a summary
    print "\nRun summary:"
    colwidth = 10
    for f, success in zip(paramfiles, results):
        if success:
            string = "success".ljust(colwidth)
        else:
            string = "fail".ljust(colwidth)
        string = string + str(f)
        print string
    return np.all(results)

def parallelRunTests(paramfiles, proc, newonly=False, require_success=False):
    """
    Run tests in parallel
    """
    
    
    args = [[paramfile, newonly, require_success] for paramfile in paramfiles]
    proc = min([cpu_count(), proc])
    print 'Spawning {0} processes'.format(proc)
    pool = Pool(proc)
    
    try:
        
        results = pool.map(_runOneTest, args, chunksize=1)
        
    finally:
        
        pool.close()
        pool.join()
        
    return results

def _runOneTest(args):
    """
    Wrapper for runOneTest for parallelization
    """
    return runOneTest(*args)

def runOneTest(paramfile, newonly=False, require_success=False):
    """
    Run a single test from the paramfile
    """
    # run the test
    
    print paramfile
    args = json.load(open(paramfile, 'r'))
    completed = args.pop('_completed', None)
    
    if completed and newonly:
        
        print "Run already completed...exiting"
        return True
    
    args['_simdir'] = runTest.setupOutputDirName(args['outputDir'], \
        args['testName'], args['configOpts'])
    
    try:
        success = runTest.runTest(**args)
    except:
        if require_success:
            raise
        success = False
    
    if success:
        
        args['_completed'] = True
    
    json.dump(args, open(paramfile,'w'), indent=4, sort_keys=True)
        
    return success

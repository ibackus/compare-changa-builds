# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 16:43:46 2016

@author: ibackus
"""
import numpy as np
import os
import pynbody
SimArray = pynbody.array.SimArray
import shutil
from distutils import dir_util
import subprocess
from multiprocessing import cpu_count
from diskpy.utils import logPrinter
import glob
import json
import errno
import copy
_runparname = 'runparams.json'

import diskpy
import config

def saveParamList(paramfiles, logsavename):
    """
    Save a list of paramfiles which can later be used to run tests
    
    Parameters
    ----------
    paramfiles : list
        A list of paths to test-run param files
    logsavename : str
        File to save the list to
    """
    with open(logsavename, 'w') as f:
        
        f.write('\n'.join(paramfiles))
        f.write('\n')
        print 'saved run param file list to', logsavename
        
def newTestConfig(name, configOpts='', testName=None):
    """
    Creates a default test-option configuration dict
    These are kwargs to be used by runTest()
    """
    if testName is None:
        
        testName=name
    
    basicTestConfig = {'directory': config.icdirs[name],
                       'configOpts': configOpts,
                       'testName': testName}
    return basicTestConfig

def makeparam(baseSaveDir, changaDir, testDict, overwrite=True, nproc=None, 
              changa_args='', charm_dir=None, runner=None, 
              userconfigdir=None, **kwargs):
    """
    Makes a run .json file which can be passed to runTest() in order to run a 
    test (basically just makes arguments for runTest.runTest and saves them to 
    baseSaveDir)
    """
    if charm_dir is None:
        charm_dir = config.charm_dir
    savename = makeTestName(testDict['testName'], testDict['configOpts'])
    savename = os.path.join(baseSaveDir, savename)
    simdir = os.path.realpath(savename)
    savename += '.json'
    
    if os.path.exists(savename) and not overwrite:
        
        print "skipping (already exists):", savename
        args = loadRunParam(savename)
    
    else:
        
        print "making:", savename
        args = copy.deepcopy(testDict)
        args['reconfigure'] = False
        args['changaDir'] = changaDir
        args['outputDir'] = baseSaveDir
        args['runner'] = runner
        args['charm_dir'] = charm_dir
        args['nproc'] = nproc
        args['changa_args'] = changa_args
        if userconfigdir is not None:
            args['userconfigdir'] = os.path.realpath(userconfigdir)
        args.update(kwargs)
        saveRunParam(args, savename)
        
    return args, savename, simdir

def runTest(directory, configOpts='', outputDir='.', 
            testName='test', paramname=None, reconfigure=True, runner=None, 
            nproc=None, changa_args='', charm_dir=None, changaDir=None, 
             **kwargs):
    """
    Will run a changa test simulation
    
    Assumes the ChaNGa binary is in the test directory
        
    Parameters
    ----------
    directory : str
        path containing the simulation to run
    configOpts : str
        Command-line arguments to pass to the ChaNGa configure script (e.g. 
        --enable-dtadjust=yes, etc.)
    outputDir : str
        Directory to save to.  The simulation will be run in a subdir of this
    testName : str
        Prefix to give the test directory name.  This should be present to 
        ensure the uniqueness of the save directory name
    paramname : str
        (optional) name of the .param file
    runner : str
        (optional) defaults to charmrun in the ChaNGa directory
    nproc : int
        Number of processors to use (used if runner=None, i.e. using the 
        default charmrun)
    changa_args : str
        Extra arguments to pass to ChaNGa
    charm_dir : str
        Directory of the charm installation (required for configuring/building)
        
    Returns
    -------
    success : bool
        Returns the success of the test.  If it the simulation was run, True
        is returned.
    """
    arguments = locals()
    assert os.path.exists(directory)
    assert os.path.exists(outputDir)
    paramname = findParam(directory, paramname)
    outputDir = setupOutputDirName(outputDir, testName, configOpts)
    safe_copy_tree(directory, outputDir)
    paramfilename = os.path.split(paramname)[-1]
    # Use absolute paths
    directory = os.path.abspath(directory)
    if changaDir is None:
        # Use ChaNGa in the run directory
        changaDir = os.path.abspath(outputDir)
    
    # Set up ChaNGa command
    if runner is None:
        
        runner = os.path.join(changaDir, 'charmrun')
        if nproc is not None:
            
            runner += ' +p{0}'.format(nproc)
            
    changa = os.path.join(changaDir, 'ChaNGa')
    runcmd = "{0} {1} {2} {3}".format(runner, changa, changa_args, paramfilename)
    print "running ChaNGa with command:"
    print runcmd
    # save run params
    runparname = os.path.join(outputDir, _runparname)
    json.dump(arguments, open(runparname, 'w'), indent=4, sort_keys=True)
    # Run ChaNGa
    cwd = os.getcwd()
    
    try:
        
        os.chdir(outputDir)
        success = diskpy.pychanga.changa_run(runcmd, log_file='changa.out',\
        return_success=True)
        
    finally:
        
        os.chdir(cwd)
    
    if success:
        
        print "Success!  Test results saved to:"
        print outputDir
    return success

# ---------------------------------------------------------------------
# Git utilities
# ---------------------------------------------------------------------

def fullsha(commit, repodir='.', verbose=True):
    """
    Get the full git SHA hash for a commit in a given repository directory
    """
    cwd = os.getcwd()
    try:
        
        os.chdir(repodir)
        p, stdout = shellRun('git rev-parse {0}'.format(commit), verbose, \
        returnStdOut=True)
        if p.returncode != 0:
            
            raise RuntimeError, 'Could not get full SHA of commit {0} in {1}'\
                .format(commit, repodir)
        
    finally:
        
        os.chdir(cwd)
        
    return stdout[0]

def formatCommit(commit, repodir='.', verbose=True):
    """
    Return a formatted 7-character commit SHA
    """
    return fullsha(commit, repodir, verbose)[0:7]


# ---------------------------------------------------------------------
# Generic utilities
# ---------------------------------------------------------------------

def mkdir_p(path):
    """
    Recursively make path (python > 2.5)
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
            
def safe_copy_tree(src, dst, **kwargs):
    """
    A small wrapper for distutils.dir_util.copy_tree. See that for documentation
    
    There is a bug in copy_tree where if you copy a tree, delete it, then try
    to copy it again it will fail.
    """
    dir_util._path_created = {}
    
    return dir_util.copy_tree(src, dst, **kwargs)
    
def shellRun(cmd, verbose=True, logfile=None, returnStdOut=False):
    """
    Try to run the basic shell command (can only run command + opts, no piping)
    """
    output = subprocess.PIPE
    p = subprocess.Popen(cmd.split(), stderr=subprocess.STDOUT, stdout=output)
    printer = logPrinter(verbose, logfile, overwrite=True)
    lines = []
    try:
        for line in iter(p.stdout.readline, ''):
            
            if line.endswith('\n'):
                line = line[0:-1]
            printer(line)
            lines.append(line)
            
        p.wait()
    finally:
        printer.close()
    
    
    if returnStdOut:
        
        return p, lines
        
    else:
        
        return p
    
def findInDir(directory, searchPattern):
    """
    Finds files matching pather searchPattern in directory
    """
    searchPattern = os.path.join(directory, searchPattern)
    results = glob.glob(searchPattern)
    results.sort()
    return results
            
# ---------------------------------------------------------------------
# Running utilities
# ---------------------------------------------------------------------

    
def findParam(directory, paramname=None):
    """
    Find and return a .param file in the directory
    """
    if paramname is None:
        
        results = findInDir(directory, '*.param')
        
        if len(results) != 1:
            
            raise RuntimeError, "Could not find .param file"
            
        paramname = results[0]
    
    else:
        
        paramname = os.path.join(directory, paramname)
        if not os.path.exists(paramname):
            
            raise ValueError, "Param file {0} does not exist".format(paramname)
            
    return paramname

def saveRunParam(param, fname):
    """
    Save the run parameters to fname as json file.  The .json extension will be
    appended to fname if not present.
    """
    if not fname.endswith('.json'):
        
        fname += '.json'
    
    directory = os.path.split(fname)[0]
    mkdir_p(directory)
    json.dump(param, open(fname, 'w'), indent=4, sort_keys=True)
    
def loadRunParam(fname):
    """
    Loads the run params from fname.  If fname doesn't end in .json will also
    try fname + .json
    """
    try:
        
        param = json.load(open(fname, 'r'))
        
    except IOError:
        
        if not fname.endswith('.json'):
            
            param = loadRunParam(fname + '.json')
            
        else:
            
            raise
            
    return param

# ---------------------------------------------------------------------
# ChaNGa building utilities
# ---------------------------------------------------------------------

def buildChanga(directory, nproc=None, copydir=None):
    """
    builds ChaNGa in directory.  nproc can be set optionally for multicore 
    building.  Defaults to n_cpu-1
    
    Can also copy the built binaries (ChaNGa and charmrun) to a directory
    copydir
    """
    if nproc is None:
        
        nproc = max([cpu_count() - 1, 1])
        
    cwd = os.getcwd()
    if  copydir is not None:
        copydir = os.path.abspath(copydir)
    
    try:
        
        os.chdir(directory)
        p = shellRun('make clean')
        p = shellRun('make -j {0}'.format(nproc))
        if p.returncode != 0 and (nproc > 1):
            # Try one more time.  ChaNGa sometimes dies during parallel builds
            # on the first try, but works on the second try
            p = shellRun('make -j {0}'.format(nproc))
        if p.returncode != 0:
            raise RuntimeError, "Could not build ChaNGa"
        
        if copydir is not None:
            
            mkdir_p(copydir)
            for f in ('ChaNGa', 'charmrun'):
                
                dest = os.path.join(copydir, f)
                print 'copying {0} to {1}'.format(f, dest)
                shutil.copy(f, dest)
        
    finally:
        
        os.chdir(cwd)
        
    return (p.returncode == 0)
        
def configureChanga(directory, configOpts='', charm_dir=None, verbose=True,
                    userconfigdir=None):
    """
    Run the ChaNGa configure script in directory, giving it the command-line
    options configOpts.  Can be silenced by setting verbose=False
    
    Raises a RuntimeError if the configuration does not exit successfully
    """
    cwd = os.getcwd()
    logfilename = os.path.abspath('configure.log')
    
    try:
        
        if charm_dir is not None:
            
            charm_dir = os.path.abspath(charm_dir)
            os.environ['CHARM_DIR'] = charm_dir
            
        os.chdir(directory)
        cmd = './configure ' + configOpts
        print 'userconfigdir', userconfigdir
        with _CopyUserConfig(userconfigdir, os.getcwd()):
            
            p = shellRun(cmd, verbose, logfilename)
            if p.returncode != 0:
                
                raise RuntimeError, "Could not configure ChaNGa"
                
            with open(logfilename,'r') as f:
                
                log = f.read()
                if 'WARNING' in log:
                    
                    raise RuntimeError, 'WARNING caught, could not configure ChaNGa'
            
            
    finally:
        
        os.chdir(cwd)
        
    return

def configBuildCommit(commit, changaDir='.', configOpts='', outputDir='.',
                      verbose=True, charm_dir=None, nproc=None, 
                      configDir='configurestuff', recompile=False, 
                      userconfigdir=None, **kwargs):
    """
    Configures and builds a given ChaNGa commit.  commit should be a git
    SHA (partial or full)
    
    Raises an error if not successful
    
    Returns the directory the binaries are saved to
    """
    outputDir = setupOutputDirName(outputDir, commit, configOpts)
    #changa directory
    changaDir = os.path.abspath(changaDir)
    # Get full commit SHA but only use first 7 characters(github style)
    commit = formatCommit(commit, changaDir, verbose)
    # Set up the directory to copy the configure scripts from
    configDir = os.path.abspath(configDir)
    configFiles = ['Makefile.in', 'configure', 'configure.ac']
    configSrc = [os.path.join(configDir, configFile) \
                 for configFile in configFiles]
    configDest = [os.path.join(changaDir, configFile) \
                  for configFile in configFiles]
    
    if not recompile and os.path.exists(os.path.join(outputDir, 'ChaNGa')):
        
        print "ChaNGa already built"
        return outputDir
        
    # Do stuff
    cwd = os.getcwd()
    try:
        os.chdir(changaDir)
        assert(shellRun('git stash').returncode == 0)
        shellRun('git checkout {0}'.format(commit))
        # copy configuration files
        for src, dest in zip(configSrc, configDest):
            shutil.copyfile(src, dest)
        configureChanga(changaDir, configOpts, charm_dir, verbose)
        buildChanga(changaDir, nproc, outputDir)
        
    finally:
        os.chdir(cwd)
    
    return outputDir

def _copy_w_permissions(src, dest):
    from subprocess import Popen
    
    p = Popen(['cp','-p','--preserve',src,dest])
    p.wait()

class _CopyUserConfig():
    """
    _CopyUserConfig(src, dest)
    
    A simple context manager for temporarily copying files from a user 
    configuration folder (containing e.g. 'configure' and 'Makefile.in') to
    a ChaNGa folder in order to override the default configure script.
    
    Parameters
    ----------
    src, dest : string
        Source and destination folders.  If either is None, then nothing 
        happens
        
    """
    flist = ['configure', 'Makefile.in']
    
    def __init__(self, src, dest):
        
        flist = self.flist
        self.backups = []
        self.copylist = []
        if (src is None) or (dest is None):
            
            return
        # Copy every file from src to dest if it exists
        for fname in flist:
            f0 = os.path.join(src, fname)
            f1 = os.path.join(dest, fname)
            if os.path.exists(f0):
                if os.path.exists(f1):
                    # backup original file
                    backup = f1 + '.backup'
                    shutil.move(f1, backup)
                    self.copylist.append(f1)
                    self.backups.append(backup)
                    print 'backing up to:', backup
                print 'copying:', f0, f1
                _copy_w_permissions(f0, f1)
    
    def __enter__(self):
        
        return
    
    def __exit__(self, *args):
        
        for f0, f1 in zip(self.backups, self.copylist):
            if os.path.exists(f0):
                # Restore the backup of the original file
                print 'restoring:', f1
                shutil.move(f0, f1)

def configBuildChanga(changaDir='.', configOpts='', testName='test', 
                      outputDir='.', copybinaries=True, verbose=True, 
                      charm_dir=None, recompile=True, userconfigdir=None,
                      **kwargs):
    """
    Builds and configures changa, optionally copying binares to the derived
    output directory
    
    Uses all but one available core
    
    **kwargs are ignored
    """
    nproc=None
    outputDir = setupOutputDirName(outputDir, testName, configOpts)
    changaDir = os.path.abspath(changaDir)
    if not recompile:
        
        if os.path.exists(os.path.join(outputDir, 'ChaNGa')) and \
        os.path.exists(os.path.join(outputDir, 'charmrun')):
            
            print 'skipping, ChaNGa already compiled'
            return True
    # Configure ChaNGa
    configureChanga(changaDir, configOpts, charm_dir, verbose, 
                    userconfigdir=userconfigdir)
    if copybinaries:
        copydir = outputDir
    else:
        copydir = None
        
    return buildChanga(changaDir, nproc, copydir)

def makeTestName(name, configOpts):
    """
    Generates a name (i.e. folder name) for a run based on its base-name 
    and the ChaNGa configure options used
    """
    name += '_' + '_'.join(configOpts.replace('--enable-', '').split(' '))
    return name
    
def setupOutputDirName(outputDir, testName, configOpts):
    """
    Sets up the output directory to use (as an absolute path)
    """
    testName = makeTestName(testName, configOpts)
    outputDir = os.path.join(outputDir, testName)
    outputDir = os.path.abspath(outputDir)
    return outputDir
    


    
    

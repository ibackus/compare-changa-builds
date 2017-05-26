# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 13:21:34 2016

@author: ibackus
"""

import numpy as np
import os
import pynbody
SimArray = pynbody.array.SimArray

import diskpy
import runTest
import config

def summarizeResults(result, testName):
    """
    Summarize test results.
    
    results should just be the direct output of the compareTests for testName
    """
    if testName in ('agora', 'agora-short'):
        result, walls = result
        print 'Mean fractional errors, averaged family-wise over all keys:'
        print '  overall:', result['full']
        print '  dark-matter:', result['dm']
        print '  gas:', result['gas']
        print '  metals:', result['metals']
        print '  stars:', result['stars']
        print 'walltime per step (run 1):', walls[0]
        print 'walltime per step (run 2):', walls[1]
        
    
    elif testName in ('sedov', 'shocktube', 'collapse'):
        
        print 'Mean fractional errors:'
        print '  density:', result['rhoErr']
        print '  temperature:', result['tempErr']
        print '  velocity:', result['vErr']
        print '  position', result['xErr']
        print 'walltime per step (run 1):', result['walls'][0]
        print 'walltime per step (run 2):', result['walls'][1]
        
    else:
        
        raise ValueError, 'No method for printing testName {}'.format(testName)

def compareTests(directories, testName, runparamname='runparams.json'):
    """
    A convenience utility to compare results for two runs of a test.  This
    is used to call one of the comparison functions.
    
    Parameters
    ----------
    directories : list or tuple-like
        The two directories containing simulations to compare
    testName : str
        The name of the test. can be:
            'shock'         - uses compareShock(...)
            'sedov'         - uses compareSedov(...)
            'agora'         - uses compareAgora(...)
            'agora-short'   - uses compareAgora(...)
            'collapse'      - uses compareCollapse(...)
    
    Returns
    -------
    results : 
        output of the functions above
    """
    if testName in ('shock', 'collapse'):
        return compareShock(directories, runparamname)
    elif testName == 'sedov':
        return compareSedov(directories, runparamname)
    elif testName == 'shocktube':
        return compareShock(directories, runparamname)
    elif testName in ('agora', 'agora-short'):
        return compareAgora(directories, runparamname)
    else:
        raise ValueError, 'No function defined to compare testName: {}'\
            .format(testName)

def compareShock(directories, runparamname='runparams.json'):
    """
    Compare the results between two shocktube tests.
    
    Can also skip the loading if directories is a list of sims and run params etc
    """
    if isinstance(directories[0], str):
        fs, ICs, runPars, lognames = loadCompareDirs(directories, runparamname)
    else:
        fs, ICs, runPars, lognames = directories

    xErr = posErr(fs, ICs)
    vErr = velErr(fs, ICs)
    gas = [f.g for f in fs]
    gasICs = [f.g for f in ICs]
    tempErr = err1D(gas, 'temp', gasICs)
    rhoErr = err1D(gas, 'rho')
    walls = walltimes(lognames)
    return {'xErr': xErr,
            'vErr': vErr,
            'tempErr': tempErr,
            'rhoErr': rhoErr,
            'walls': walls}
    
def compareSedov(directories, runparamname='runparams.json', vthresh=1e-9):
    """
    Compare the results between two sedov tests.  Very similar to compareShock,
    but filter out particles which aren't moving much (haven't had the blast
    hit them yet)
    
    If a particle in any of the final results has velocity > vthresh*v.max() 
    it will be kept
    """
    fs, ICs, runPars, lognames = loadCompareDirs(directories, runparamname)
    
    v = vectorMag3D(fs[0]['vel'])
    mask = (v >= (v.max() * vthresh))
    
    for f in fs[1:]:
        
        v = vectorMag3D(f['vel'])
        mask = (mask) | (v >= (v.max() * vthresh))
        
    fs = [f[mask] for f in fs]
    ICs = [f[mask] for f in ICs]
    
    return compareShock((fs, ICs, runPars, lognames), runparamname)

def compareAgora(directories, runparamname='runparams.json'):
    """
    Compare the results between two agora tests
    
    directories can be a list of directories or a list of simsnaps
    
    Returns a dict of 'scores'.  scores are the mean error for different 
    quantities on a family-level basis, i.e. position and velocity for 
    dark matter, gas is position, velocity, temperature, and density,
    and metals is for all metals arrays
    """
    
    fs, ICs, runPars, lognames = loadCompareDirs(directories, runparamname)
    # shorten the snapshots
    allSnaps = intersectSnaps(fs+ICs)
    fs = allSnaps[0:2]
    ICs = allSnaps[2:]
    scores = {}
    
    print '\nComparing full simulation'
    xErr = posErr(fs, ICs)
    vErr = velErr(fs, ICs)
    scores['full'] = np.mean((xErr, vErr))
    
    print '\nComparing dark matter (this is pass trivially)'
    darkMatter = intersectSnaps([f.dm for f in fs + ICs])
    darkMatter, darkMatterICs = (darkMatter[0:2], darkMatter[2:])
    xErr = posErr(darkMatter, darkMatterICs)
    vErr = velErr(darkMatter, darkMatterICs)
    scores['dm'] = np.mean((xErr, vErr))
    
    print '\nComparing gas'
    gas = intersectSnaps([f.g for f in fs + ICs])
    gas, gasICs = (gas[0:2], gas[2:])
    xErr = posErr(gas, gasICs)
    vErr = velErr(gas, gasICs)
    tempErr = err1D(gas, 'temp', gasICs)
    rhoErr = err1D(gas, 'rho')
    scores['gas'] = np.nanmean((xErr, vErr, tempErr, rhoErr))
    otherkeys = ['metals',
                 'HI',
                 'OxMassFracdot',
                 'HeI',
                 'FeMassFracdot',
                 'Metalsdot',
                 'ESNRate',
                 'FeMassFrac',
                 'HeII',
                 'OxMassFrac']
    metalsErrs = []
    # Get keys present in both simulations
    all_keys = list(set.intersection(*[set(g.all_keys()) for g in gas]))
    for key in otherkeys:
        if key in all_keys:
            metalsErrs.append(err1D(gas, key))
        else:
            print 'array {} missing'.format(key)
    scores['metals'] = np.nanmean(metalsErrs)
    
    print '\n Comparing stars'
    stars = intersectSnaps([f.s for f in fs + ICs])
    stars, starICs = (stars[0:2], stars[2:])
    xErr = posErr(stars, starICs)
    vErr = velErr(stars, starICs)
    scores['stars'] = np.nanmean((xErr, vErr))
    
    print '\nWalltime:'
    
    walls = walltimes(lognames)
    
    return scores, walls

# ---------------------------------------------------------------------
# Generic utilities
# ---------------------------------------------------------------------

def notNanInf(x):
    """
    Return a masked version of x, including only elements that are not nan
    and are non inf
    """
    mask = (~np.isnan(x)) & (~np.isinf(x))
    return x[mask]
    
def nanInfMean(x):
    """
    Return mean of x, excluding nan and inf vals
    """
    return notNanInf(x).mean()

def simSize(f):
    """
    estimates 'size' of simulation
    """
    return np.sqrt(np.sum(f['pos'].std(0)**2))

def vectorMag3D(x):
    """
    Magnitude of a 3d vector
    """
    return np.sqrt((x**2).sum(1))
    
def walltimes(lognames, verbose=True):
    """
    Get mean walltimes in 2 directories
    """
    outs = [diskpy.pychanga.walltime(log, verbose=False).mean() for log in lognames]
    
    if verbose:
        
        colsize = 16
        words = ['walltime'.ljust(colsize), 'log file']
        print ''.join(words)
        for walltime, logname in zip(outs, lognames):
            
            print ''.join([str(walltime).ljust(colsize), logname])
            
    return outs
    
def readLines(fname):
    """
    Reads lines from file fname, ignoring lines commented by #, and returns 
    as a list
    """
    with open(fname, 'r') as f:
        
        flist = []
        for line in f:
            
            line = line.strip()
            if line[0] != '#':
                
                flist.append(line)
                
    return flist
    
def getLogName(directory, paramname=None):
    """
    gets the changa .log filename if possible
    """
    paramname = runTest.findParam(directory, paramname)
    param = diskpy.utils.configparser(paramname, 'param')
    fprefix = diskpy.pychanga.getpar('achOutName', param)
    logname = fprefix + '.log'
    return os.path.join(directory, logname)
    
def findSnapshots(directory, paramname=None):
    """
    Finds the output snapshots in directory and the output .log file
    """
    
    paramname = runTest.findParam(directory, paramname)
    param = diskpy.utils.configparser(paramname, 'param')
    fprefix = diskpy.pychanga.getpar('achOutName', param)
    fnames = diskpy.pychanga.get_fnames(fprefix, directory)
    return fnames
    
def loadResults(directories, paramname=None):
    """
    Loads the final output snapshots in 'directories'
    """
    
    fnames = [findSnapshots(directory, paramname) for directory in directories]
    resultnames = [flist[-1] for flist in fnames]
    
    fs = [pynbody.load(fname) for fname in resultnames]
    
    return fs
    
def loadICs(directories, paramname=None):
    """
    """
    if hasattr(directories, '__iter__'):
        
        return [loadICs(directory, paramname) for directory in directories]
    
    directory = directories
    paramname = runTest.findParam(directory, paramname)
    param = diskpy.utils.configparser(paramname, 'param')
    ICname = param['achInFile']
    ICname = os.path.join(directory, ICname)
    IC = pynbody.load(ICname, paramfile=paramname)
    # Access the iord
    getIord(IC)
    return IC
    
    
def loadRunPars(directories, runparams='runparams.json'):
    """
    Loads the run params in directories
    """
    runParNames = [os.path.join(directory, runparams) for directory in directories]
    runPars = [runTest.loadRunParam(runParName) for runParName in runParNames]
            
    return runPars
    
def loadArgDicts(fnames):
    """
    Load the arg dicts (basically any dictionary saved via json) in fnames.
    fnames can be a str or a list of strings
    """
    
    if hasattr(fnames, '__iter__'):
        
        return np.array([loadArgDicts(fname) for fname in fnames])
        
    return runTest.loadRunParam(fnames)
    
def getFromDictList(dicts, key, default=None):
    """
    Retrieve value of key in a list of dicts, returning a default value if not
    present.  Return as a numpy array
    """
    return np.array([d.get(key, default) for d in dicts])
    
def flattenDictList(dicts, default=None):
    """
    From a list of dictionaries, return a single dict where keys have been 
    flattened to numpy arrays, replacing non-present keys with default value
    """
    allkeys = set()
    for d in dicts:
        
        allkeys = allkeys.union(set(d.keys()))
        
    allkeys = list(allkeys)
    
    flattened = {}
    
    for key in allkeys:
        
        flattened[key] = getFromDictList(dicts, key, default)
        
    return flattened
        
    
def loadCompareDirs(directories, runparamname='runparams.json'):
    """
    Loads final results and run parameters of two comparison directories
    """        
    runPars = loadRunPars(directories, runparamname)
    fs = loadResults(directories)
    lognames = [getLogName(directory) for directory in directories]
    ICs = loadICs(directories)
    
    return fs, ICs, runPars, lognames

def getIord(f):
    """
    Tries to load particle iords if available, otherwise defaults to 
    0, 1, 2, ...
    """
    try:
        
        return f['iord']
        
    except KeyError:
        
        
        f['iord'] = np.arange(len(f))
        return f['iord']
    
def intersectSnaps(fs, verbose=False):
    """
    Returned index sub-snaps of only particles present in all snapshots in 
    fs
    
    Requires 'iord' key
    """
    common = getIord(fs[0])
    for f in fs[1:]:
        
        common = np.intersect1d(common, getIord(f), assume_unique=True)
    
    unique = [np.setdiff1d(getIord(f), common, assume_unique=True) for f in fs]
    fsSorted = [f[getIord(f).argsort()] for f in fs]
    fsShort = []
    
    for i, fSorted in enumerate(fsSorted):
        
        mask = np.ones(len(fSorted), dtype=bool)
        remove = unique[i]
        if verbose:
            
            print "removing {0} from {1}".format(remove, i)
            
        for r in remove:
            
            ind = np.argwhere(getIord(fSorted) == r)[0][0]
            mask[ind] = False
            
        fsShort.append(fSorted[mask])
        
    return fsShort
# ---------------------------------------------------------------------
# Error/comparison utilities
# ---------------------------------------------------------------------
def dist(f1, f2):
    """
    distance between particles in 2 sims (must be same length)
    """
    return vectorMag3D(f1['pos'] - f2['pos'])
    
def fracDiff3D(x1, x2):
    """
    fractional difference between 2 3d vectors
    """
    x1mag = vectorMag3D(x1)
    x2mag = vectorMag3D(x2)
    dx = vectorMag3D(x2 - x1)
    return dx/(0.5*(x1mag + x2mag))
    
def fracDiff1D(x1, x2):
    """
    Fractional difference between 2 1d vectors
    """
    dx = abs(x2 - x1)
    meanx = 0.5*(abs(x1) + abs(x2))
    return dx/meanx

def posErr(fs, ICs, verbose=True):
    """
    Estimate the relative error in position between snapshots fs[0] and fs[1]
    This is estimated by the mean of <the distance between particles in the two
    sims, normalized by the distance travelled by the particles>
    """
    f1, f2 = fs
    IC1, IC2 = ICs
    d12 = dist(f1, f2)
    d1 = dist(f1, IC1)
    d2 = dist(f2, IC2)
    dmean = 0.5 * (d1 + d2)
    errors = d12/dmean
    xErr = nanInfMean(errors)
    
    if verbose:
        
        print 'Relative position error:', xErr
        fracZero = zeroFraction(errors)
        print "   fraction of identical positions", fracZero
    
    return xErr
    
def velErr(fs, ICs, verbose=True):
    """
    Estimates the relative velocity error between two simulations
    """
    v12diff = vectorMag3D(fs[0]['vel'] - fs[1]['vel'])
    vdiffs = [vectorMag3D(f['vel'] - IC['vel']) for f, IC in zip(fs, ICs)]
    vdiffmean = 0.5 * (vdiffs[0] + vdiffs[1])
    errors = v12diff/vdiffmean
    vErr = nanInfMean(errors)
    
    if verbose:
        
        print 'Relative velocity err:', vErr
        fracZero = zeroFraction(errors)
        print "   fraction of identical velocities:", fracZero
    
    return vErr
    
def err1D(fs, key, ICs=None, verbose=True):
    """
    Estimate the mean error between fs[0][key] and fs[1][key] and ICs
    
    Error is normalized by the mean difference with ICs if supplied, else
    its normalized by the value of f[key]
    """
    f1, f2 = fs
    
    if ICs is not None:
        IC1, IC2 = ICs
        diff12 = abs(f1[key] - f2[key])
        diffs = [abs(IC[key] - f[key]) for IC, f in zip(ICs, fs)]
        diffmean = 0.5 * (diffs[0] + diffs[1])
        errors = diff12/diffmean
        err = nanInfMean(errors)
    else:
        errors = fracDiff1D(f1[key], f2[key])
        err = nanInfMean(errors)
    
    if verbose:
        
        print "Relative '{0}' error:".format(key), err
        fracZero = zeroFraction(errors)
        print "   fraction of identical elements:", fracZero
        
    return err
        
def zeroFraction(x, neps=3):
    """
    For x being a difference between two floats, check to see if 
    abs(x) < neps*eps where eps is the float precision
    """
    eps = neps * np.finfo(x.dtype).eps
    x = notNanInf(x)
    zeros = (abs(x) < eps).sum()
    return zeros/float(x.size)
    


    

# compare-changa-builds
python tools to compare test results for different builds of changa

The main functionality of this package is to allow the user to run multiple basic test simulations (e.g. the classic ChaNGa sedov or collapse tests) with multiple versions of ChaNGa and compare the results.  Multiple tests can easily be run on the same simulation using different combinations of compile flags (this package can build and run ChaNGa).  This package was developed to aid in refactoring some of the SPH calculations.

A typical work flow would be:
* Make some changes to a branch of ChaNGa
* select tests you want to run (agora, sedov, shocktube, etc...)
* choose what compile time flags you want for the tests.  One run could have `--enable-rtforce=no` and the other could use `--enable-rtforce=yes --enable-dtadjust=no`
* Define the versions of ChaNGa you want to run (these should be multiple copies of the repo on your computer)
* Run and compare the tests.  You can use the tools here to automatically configure and build ChaNGa for each test and to run all the tests then compare their results.

## Getting started

### Install

#### Install dependencies
* numpy and scipy
* [pynbody](https://github.com/pynbody/pynbody)
* [diskpy](https://github.com/ibackus/diskpy)
* ChaNGa.  Preferably you should have two copies of the ChaNGa repository on you computer.  The idea here is to configure, build, and run from two different versions of ChaNGa simultaneously in order to see if any changes have broken your code.

#### Clone this repository
```
git clone https://github.com/ibackus/compare-changa-builds/
```
#### Setup
First, run the `setup.sh` script.

Next, update the configuration file `compchanga/_user_config.py`.  You'll need to set the charm directory there.

Finally, add the cloned repo directory to your PYTHONPATH.

### Examples
READ THROUGH the examples before running them.  They need some configuring and playing with to work and are mostly meant to show you how to use the tools here.

After setting up, check out the examples in the `examples/` folder.  The simplest example is the script `agora_test_example.py`.  This will run a short version of the agora test with different compile-time options.  

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 23 12:08:24 2017

@author: ibackus
"""
import os
_directory = os.path.dirname(os.path.realpath(__file__))

# -------------------------------------------
# Settings
# -------------------------------------------
# Charm directory (needed to build ChaNGa)
charm_dir='/usr/lusers/ibackus/charm'
# Base directory containing the test ICs
ICBaseDir = '../tests'
# Directories containing test ICs (sub-directories of ICBaseDir)
icdirs = {'agora': 'agora',
          'sedov': 'sedov',
          'collapse': 'collapse',
          'shocktube': 'shocktube',
          'agora-short': 'agora-short'}
# -------------------------------------------
# Setup
# -------------------------------------------
# Set-up the icdirs
ICBaseDir = os.path.join(_directory, ICBaseDir)
for k, v in icdirs.iteritems():
    icdirs[k] = os.path.join(ICBaseDir, v)
# Keep a list of test names
tests = icdirs.keys()

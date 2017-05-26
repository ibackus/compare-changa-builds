#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 23 12:08:24 2017

@author: ibackus
"""
import os
_directory = os.path.dirname(os.path.realpath(__file__))

execfile(os.path.join(_directory, '_default_config.py'))
execfile(os.path.join(_directory, '_user_config.py'))
# -------------------------------------------
# Setup
# -------------------------------------------
# Set-up the icdirs
ICBaseDir = os.path.join(_directory, ICBaseDir)
for k, v in icdirs.iteritems():
    icdirs[k] = os.path.join(ICBaseDir, v)
# Keep a list of test names
tests = icdirs.keys()

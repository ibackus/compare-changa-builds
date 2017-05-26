#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Contains default configurations.  Users should NOT CHANGE THIS FILE but instead
change _user_config.py

This is executed by config.py before executing _user_config.py.  Override or
change defaults in _user_config.py

Created on Thu May 25 17:33:43 2017

@author: ibackus
"""

# -------------------------------------------
# Settings
# -------------------------------------------
# Base directory containing the test ICs
ICBaseDir = '../tests'
# Directories containing test ICs (sub-directories of ICBaseDir)
icdirs = {'agora': 'agora',
          'sedov': 'sedov',
          'collapse': 'collapse',
          'shocktube': 'shocktube',
          'agora-short': 'agora-short'}

# -*_ coding: utf-8 -*-

import typing
from typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys
###
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###
import argparse
import contextlib
from   datetime import datetime
import getpass
import logging
import toml as tomllib
import paramiko
import sqlite3
import re
import fcntl
mynetid = getpass.getuser()

###
# Installed libraries.
###


###
# From hpclib
###
import linuxutils
from   sloppytree import SloppyTree
import sqlitedb
from   sqlitedb import SQLiteDB
from   urdecorators import trap
from   urlogger import URLogger, piddly
from   dorunrun import dorunrun

###
# imports and objects that are a part of this project
###

from threshold_parser import parse_threshold_main

###
# Global objects and initializations
###
verbose = False

###
# Credits
###
__author__ = 'George Flanagin, João Tonini'
__copyright__ = 'Copyright 2024'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin, João Tonini'
__email__ = ['gflanagin@richmond.edu', 'jtonini@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'

####
# Step 1: Parse the threshold string to extract the value and unit.
###

@trap
def convert_threshold_main(threshold_value: float, threshold_unit: str) -> float:
    """
    Convert the threshold value to the appropriate format for xfs_quota command.

    Args:
        value (float): The threshold value.
        unit (str): The unit of the threshold ('T' for terabytes or 'G' for gigabytes).

    Returns:
        str: The threshold value in the appropriate format for xfs_quota (e.g., '2' for 2 terabytes).
    """
    if threshold_unit == 'T':
        return float(threshold_value)
    elif threshold_unit == 'G':
        return round(float(threshold_value / 1024), 3)
    else:
        raise ValueError("Invalid threshold unit. Please specify 'T' for terabytes or 'G' for gigabytes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="convert_threshold_main", description="Convert threshold value to appropriate format")
    parser.add_argument('-thv', '--threshold_value', type=float, required=True, help="Threshold value specified by the user (e.g., intenger or floats)")
    parser.add_argument('-thu', '--threshold_unit', type=str, required=True, help="Threshold unit specified by the user (e.g. T or G)")
    
    args = parser.parse_args()

    formatted_threshold_value = convert_threshold_main(float(args.threshold_value), args.threshold_unit)
    print(f"Formatted threshold: {formatted_threshold_value} Tb")

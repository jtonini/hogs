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
def parse_threshold_main(threshold_str:str) -> str:
    """
    Parameters:
        threshold_str (str): The threshold string specified by the user (e.g., '2T' for 2 terabytes).

    Returns:
        tuple: A tuple containing the threshold value as a float and the unit as a string ('T' or 'G').
    """
    
    match = re.match(r'^(\d+)([TG])$', threshold_str)
    if match:
        threshold_value = float(match.group(1))
        threshold_unit = match.group(2)
        return threshold_value, threshold_unit
    else:
        raise ValueError("Invalid threshold format. Please specify a number followed by 'T' or 'G'.")

if __name__ == "__main__":
    # Check if threshold is provided as command-line arguments
   # if len(sys.argv) != 1:
   #     print("Usage: python parse_threshold_main.py <threshold>")
   #     sys.exit(1)

    parser = argparse.ArgumentParser(prog="parse_threshold_main", description="Filtering users with usage exceeding a specified threshold")
    parser.add_argument('-th', '--threshold', type=str, required=True, help="Threshold to filter users by stored data.")
 
    myargs = parser.parse_args()

    # Call parse_threshold_main function with provided parameters
    threshold_value, threshold_unit = parse_threshold_main(myargs.threshold)
    print(f"Parsed threshold value: {threshold_value}, unit: {threshold_unit}")

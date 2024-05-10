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
import argparse
import re

def parse_threshold_main(threshold:str) -> tuple:
    """
    Parse the threshold string to extract the value and unit.

    Parameters:
        threshold_str (str): The threshold string specified by the user (e.g., '2T' for 2 terabytes).

    Returns:
        tuple: A tuple containing the threshold value as a float and the unit as a string ('T', 'G', 'M', or 'K').
    """

    match = re.match(r'^(\d+(\.\d+)?)([TGMK])$', threshold)
    if match:
        threshold_value = float(match.group(1))
        threshold_unit = match.group(3)
        return threshold_value, threshold_unit
    else:
        raise ValueError("Invalid threshold format. Please specify a number followed by 'T', 'G', 'M', or 'K'.")

def convert_threshold_main(threshold_value: float, threshold_unit: str) -> float:
    """
    Convert the threshold value to the appropriate format for xfs_quota command.

    Args:
        threshold_value (float): The threshold value.
        threshold_unit (str): The unit of the threshold ('T' for terabytes, 'G' for gigabytes, 'M' for megabytes, or 'K' for kilobytes).

    Returns:
        float: The threshold value in terabytes.
    """
    if threshold_unit == 'T':
        return threshold_value
    elif threshold_unit == 'G':
        return round(threshold_value / 1024, 3)
    elif threshold_unit == 'M':
        return round(threshold_value / (1024 * 1024), 3)
    elif threshold_unit == 'K':
        return round(threshold_value / (1024 * 1024 * 1024), 3)
    else:
        raise ValueError("Invalid threshold unit. Please specify 'T', 'G', 'M', or 'K'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse and convert threshold value.")
    parser.add_argument('-th', '--threshold', type=str, required=True, help="Threshold string specified by the user (e.g., '2T' for 2 terabytes).")
    args = parser.parse_args()

    threshold_value, threshold_unit = parse_threshold_main(args.threshold)
    print(f"Parsed threshold value: {threshold_value}, unit: {threshold_unit}")

    formatted_threshold_value = convert_threshold_main(threshold_value, threshold_unit)
    print(f"Formatted threshold: {formatted_threshold_value} Tb")


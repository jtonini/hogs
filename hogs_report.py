# -*_ coding: utf-8 -*-

import typing
from typing import *

min_py = (3, 11)

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
import tomllib
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
from   Sloppytree import Sloppytree

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
    def parse_threshold(threshold_str) -> str:

    """
    Parameters:
        threshold_str (str): The threshold string specified by the user (e.g., '2T' for 2 terabytes).

    Returns:
        tuple: A tuple containing the threshold value as a float and the unit as a string ('T' or 'G').
    """
    
    match = re.match(r'^(\d+)([TG])$', threshold_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        return value, unit
    else:
        raise ValueError("Invalid threshold format. Please specify a number followed by 'T' or 'G'.")

###
# Step 2: Convert the threshold value to the appropriate format for the xfs_quota command.
###

@trap
def convert_threshold(value, unit) -> str:

    """
    Parameters:
        value (float): The threshold value.
        unit (str): The unit of the threshold ('T' for terabytes or 'G' for gigabytes).

    Returns:
        str: The threshold value in the appropriate format for xfs_quota (e.g., '2' for 2 terabytes).
    """

    if unit == 'T':
        return str(value)
    elif unit == 'G':
        return str(value * 1024)
    else:
        raise ValueError("Invalid threshold unit. Please specify 'T' for terabytes or 'G' for gigabytes.")

###
# Step 3. Perform a hog report.
###

@trap
def hogs_main(server:str, directory:str, threshold_value:float, threshold_unit:str) -> str:
    
    """
    Perform a hog report for a specified directory on a remote host via SSH, filtering users with usage 
    exceeding a specified threshold, and store the results in a SQLite3 database.

    Parameters:
        server (str): The hostname or IP address of the remote server.
        directory (str): The directory path for which to generate the hog report.
        threshold_value (float): The threshold value for usage.
        threshold_unit (str): The unit of the threshold ('T' for terabytes or 'G' for gigabytes).
    """
    
    print(f"Generating hog report for {directory} on server '{server}' with threshold {threshold_value}{threshold_unit}")
    
    # Convert threshold to appropriate format for xfs_quota command
    threshold = convert_threshold(threshold_value, threshold_unit)
    
    # Execute command on remote host via SSH; TO DO: how to include forkssh to perform the ssh part?
    cmd = f"sudo xfs_quota -x -c 'report -u -ah' {}"
    
    result=Sloppytree(dorunrun("""ssh {server} "{cmd}" """, result_type=dict))
    if not result.OK:
        # in subprocess
#       if "Permission denied" in error.decode():
             
        pass

    for line in result.stdout.split():
        user, space, _0, _1, _2, _3 = line.split()
        space = linuxutils.byte_size(space)
    
    return "Hog report generated successfully and stored in hog_report.db"

if __name__ == "__main__":
    # Check if server name, directory, and threshold are provided as command-line arguments
    if len(sys.argv) != 4:
        print("Usage: python hog_report.py <server> <directory> <threshold>")
        sys.exit(1)

    # Parse command-line arguments; TO DO: implement in argparse
    #server = sys.argv[1]
    #directory = sys.argv[2]
    #threshold_value, threshold_unit = parse_threshold(sys.argv[3])

   parser = argparse.ArgumentParser(prog="hogs_main",
                                    description="Filtering users with usage exceeding a specified threshold")
    parser.add_argument('-s', '--server', type=str, required=True,
                        help="Host name or IP address of one or more workstations.")
    parser.add_argument('-d', '--directory', type=str, required=True, 
                        help="Directory(ies) to be filtered")
    parser.add_argument('-th', '--threshold', type=str, default="",
                        help="Threshold to filter users by stored data.")
 
   myargs = parser.parse_args()
   verbose = myargs.verbose

    # Call hog_report function with provided parameters
    hogs_main(server, directory, threshold_value, threshold_unit)


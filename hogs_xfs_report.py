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
from   sloppytree   import SloppyTree
import sqlitedb
from   sqlitedb     import SQLiteDB
from   urdecorators import trap
from   urlogger     import URLogger, piddly
from   dorunrun     import dorunrun

###
# imports and objects that are a part of this project
###

from    threshold_parser    import  parse_threshold_main    as  parse_threshold
from    threshold_parser    import  convert_threshold_main  as  convert_threshold

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

@trap
def hogs_xfs_main(server:str, directory_path:str) -> dict:
    
    """
    Perform a hog report for a specified directory with XFS filesystem on a remote host via SSH, filtering users with usage exceeding a specified threshold, and store the results in a SQLite3 database.

    Parameters:
        server (str): The hostname or IP address of the remote server.
        directory (str): The directory path for which to generate the hog report.
    """
    
    print(f"Generating quota report for {directory_path} on server '{server}'")
    
    # Execute command on remote host via SSH; TO DO: how to include the ssh part?
    cmd = f"""ssh -o ConnectTimeout=1 root@{server} 'sudo xfs_quota -x -c "report -u -ah" {directory_path}'"""    
    #result=SloppyTree(dorunrun(""" ssh {server} "{cmd}" """, return_datatype=dict)) # how to ssh as root?
    result=SloppyTree(dorunrun(cmd, return_datatype=dict))
    #if not result.OK:
        # in subprocess
#       if "Permission denied" in error.decode():
             
    #    pass

    #for line in result.stdout.split():
    #directory_name = directory_line[start_index:end_index]    user, space, _0, _1, _2, _3 = line.split()
    #    space = linuxutils.byte_size(space)
    
    # Extract directory information
    directory_line = result['stdout'].split('\n')[0]
    start_index = directory_line.find('/') + 1
    end_index = directory_line.find(' (')  # Extracting the directory name from the line
    
    directory_name = directory_line[start_index:end_index]

    # Extract the lines containing user quota information
    output = result['stdout'].split('\n')[3:]
    
    # Initialize an empty list to store extracted information
    user_data = []    

    # Iterate over each line to extract user quota information
    
    for line in output:
        # Split the line into components
        if line: # Check if the line is not empty
            parts = line.split()
            if len(parts) >= 2:
                user_data.append(parts)

    # Extract directory, user, and quota used
    quota_info = []
    
    # Use a set to keep track of unique lines
    unique_lines = set()

    for line in user_data:
        if len(line) < 2:
            continue  # Skip lines with insufficient data
    
        if line[0] == '----------' and line[1] == '---------------------------------':
            continue  # Skip separator lines
    
        user = line[0]
        quota_used = line[1]
        threshold_value, threshold_unit = parse_threshold(quota_used)
        quota_used_tb = convert_threshold(threshold_value, threshold_unit)
   
        # Create a unique string representation of the line
        line_str = f"{directory_name} {user} {quota_used_tb}"
    
        # Check if the line is unique, if not, skip it
        if line_str in unique_lines:
            continue

        # Add the line to the set of unique lines
        unique_lines.add(line_str)

        quota_info.append({'directory': directory_name, 'user': user, 'quota_used_tb': quota_used_tb})

    # Print the extracted information
    for info in quota_info[1:]:
        print(info)
    #return "Hog report generated successfully and stored in hog_report.db"
    return quota_info

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog="hogs_xfs_main", description="Filtering users with usage")
    parser.add_argument('-s', '--servers', nargs="+", required=True, help="List of servers or host name or IP address of one or more workstations.")
    parser.add_argument('-d', '--directory_path', type=str, required=True, help="Directories to be filtered")
    myargs = parser.parse_args()
    #verbose = myargs.verbose
    
    for server in myargs.servers:

    # Call hog_report function with provided parameters
        hogs_xfs_main(server, myargs.directory_path)

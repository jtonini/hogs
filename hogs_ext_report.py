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
from    threshold_parser    import  parse_threshold_main    as  parse_threshold
from    threshold_parser    import  convert_threshold_main  as  convert_threshold

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

from threshold_parser    import parse_threshold_main as parse_threshold
from threshold_parser    import convert_threshold_main as convert_threshold


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
def parse_output(output: str) -> dict:
    directory_line = output.split('\n')[0]
    words = re.split(r'\W+', directory_line)
    directory_name = words[-1]

    output_lines = output.split('\n')[3:]
    output_lines = output_lines[2:]

    user_data = []
    unique_lines = set()

    for line in output_lines:
        if line:  # Check if the line is not empty
            parts = line.split()
            if len(parts) >= 2:
                user_data.append(parts)

    quota_info = []

    for line in user_data:
        if len(line) < 2:
            continue  # Skip lines with insufficient data

        user = line[0]
        blocks = line[2]

        quota_used_tb = round(int(blocks) * block_size / 1024**4, 3)  # For TB

        line_str = f"{directory_name} {user} {quota_used_tb}"

        if line_str in unique_lines:
            continue

        unique_lines.add(line_str)

        quota_info.append({'directory': directory_name, 'user': user, 'quota_used_tb': quota_used_tb})

    return quota_info

@trap
def hogs_ext_main(server: str, directory_path: str) -> dict:
    """
    Perform a hog report for a specified directory with XFS filesystem on a remote host via SSH, filtering uses    with usage exceeding a specified threshold, and store the results in a SQLite3 database.

    Parameters:
        server (str): The hostname or IP address of the remote server.
        directory (str): The directory path for which to generate the hog report.
        threshold: value (float) for usage and unit (str) ('T' for terabytes or 'G' for gigabytes).
    """
    
    print(f"Generating quota report for {directory_path} on server '{server}'")
    
    # Execute command on remote host via SSH; TO DO: how to include the ssh part?
    cmd = f"""ssh -o ConnectTimeout=1 root@{server} 'repquota {directory_path}'"""    
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
    words = re.split(r'\W+', directory_line)   
    directory_name = words[-1]

    # Extract the lines containing user quota information
    output = result['stdout'].split('\n')[3:]
    output = output[2:]    
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="hogs_ext_main", description="Filtering users with usage exceeding a specified threshold")
    parser.add_argument('-s', '--servers', nargs="+", required=True, help="List of servers or host name or IP address of one or more workstations.")
    parser.add_argument('-d', '--directory_path', type=str, required=True, help="Directory(ies) to be filtered")
    myargs = parser.parse_args()

    for server in myargs.servers:
        hogs_ext_main(server, myargs.directory_path)

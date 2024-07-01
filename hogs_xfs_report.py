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
    ssh_cmd = f"""sudo xfs_quota -x -c "report -u -ah" {directory_path}"""    
    #result=SloppyTree(dorunrun(""" ssh {server} "{cmd}" """, return_datatype=dict)) # how to ssh as root?
    try:
        # Try connecting as root first
        result=SloppyTree(dorunrun(f"ssh -o ConnectTimeout=1 root@{server} '{ssh_cmd}'", return_datatype=dict))
        if result.OK:
            return parse_xfs_output(result.stdout)
    except:
        print("Connection as root failed")
    
    try:
        # If connecting as root fails, try connecting as installer
        cmd = f"""sudo xfs_quota -x -c "report -u -ah" {directory_path}"""
        ssh_cmd = f"""ssh spdrstor01 '{cmd}'"""
        result = dorunrun(f"ssh -o ConnectTimeout=1 installer@{server} '{ssh_cmd}'", return_datatype=dict)
        if result.OK:
            return parse_output(result.stdout)
    except:
        print("Connection as installer failed.")

    # If both attempts fail, print a message and return an empty dictionary
        print("Failed to connect to the server.")
        return {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="hogs_xfs_main", description="Filtering users with usage")
    parser.add_argument('-s', '--servers', nargs="+", required=True, help="List of servers or host name or IP address of one or more workstations.")
    parser.add_argument('-d', '--directory_path', type=str, required=True, help="Directories to be filtered")
    myargs = parser.parse_args()

    for server in myargs.servers:
        # Call hog_report function with provided parameters
        hogs_xfs_main(server, myargs.directory_path)

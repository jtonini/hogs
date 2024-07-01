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
def parse_xfs_output(output):
    # Extract directory information
    directory_line = output.split('\n')[0]
    start_index = directory_line.find('/') + 1
    end_index = directory_line.find(' (')  # Extracting the directory name from the line
    directory_name = directory_line[start_index:end_index]

    # Extract the lines containing user quota information
    user_data = output.split('\n')[3:]

    # Initialize an empty list to store extracted information
    quota_info = []

    # Use a set to keep track of unique lines
    unique_lines = set()

    for line in user_data:
        # Split the line into components
        if line: # Check if the line is not empty
            parts = line.split()
            if len(parts) >= 2:
                user = parts[0]
                quota_used = parts[1]
                threshold_value, threshold_unit = parse_threshold(quota_used)
                quota_used_tb = convert_threshold(threshold_value, threshold_unit)

                # Create a unique string representation of the line
                line_str = f"{directory_name} {user} {quota_used_tb}"

                # Check if the line is unique, if not, skip it
                if line_str not in unique_lines:
                    unique_lines.add(line_str)
                    quota_info.append({'directory': directory_name, 'user': user, 'quota_used_tb': quota_used_tb})

    # Print the extracted information
    for info in quota_info:
        print(info)

    return quota_info


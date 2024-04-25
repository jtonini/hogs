# -*- coding: utf-8 -*-
import typing
from   typing import *

min_py = (3, 9)

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
import getpass
mynetid = getpass.getuser()

###
# Installed libraries.
###

import re

###
# From hpclib
###
import linuxutils
from   urdecorators import trap
from   sloppytree import SloppyTree
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
__author__ = 'George Flanagin and João Tonini'
__copyright__ = 'Copyright 2024'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin and João Tonini'
__email__ = ['gflanagin@richmond.edu' 'jtonini@richmond.com']
__status__ = 'in progress'
__license__ = 'MIT'

@trap
def is_xfs_filesystem(directory_path:str) -> bool:
    """
    Check if the specified directory is on an XFS file system.

    Args:
    directory_path (str): The path to the directory to check.

    Returns:
    bool: True if the directory is on an XFS file system, False otherwise.
    """
    # command to get filesystem type
    cmd = f"stat -f -c %T {directory_path}"
    result=dorunrun(cmd, return_datatype=str)
    if re.search("xfs", result):
        return True
    else:
        return False # return false if no line contains "xfs"; and test if it is 'ext' (To do)

@trap
def is_xfs_quota_enabled(directory_path:str) -> bool:
    """
    Check if quota is enabled for the specified directory path.

    Args:
    directory_path (str): The directory path to check, e.g. /home.

    Returns:
    bool: True if quota is enabled, False otherwise.
    """
    # mount command to check if quota options are present
    cmd = f"mount -t xfs"
    result = dorunrun(cmd, return_datatype=str)
    #if re.search(r"/home", result) and re.search(r"\busrquota\b", result) or re.search(r"\bgrpquota\b", result):
    for line in result.splitlines():
        if directory_path in line and "xfs" in line and ("usrquota" in line or "grpquota" in line):
            return True
    #    return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if a specified directory is on an XFS file system and if quota is enabled.")
    parser.add_argument('-d', '--directory', type=str, required=True, help="The directory path to check.")

    args = parser.parse_args()

    if is_xfs_filesystem(args.directory):
        print("XFS file system detected.")
        if is_xfs_quota_enabled(args.directory):
            print("Quota is enabled.")
        else:
            print("Quota is not enabled.")
    else:
        print("Not an XFS file system.")


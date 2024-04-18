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
import shutil
import socket
import subprocess

###
# Installed libraries.
###


###
# From hpclib
###

import linuxutils
from   urdecorators import trap
from   sloppytree import SloppyTree
from   dorunrun import dorunrun
from   urdecorators import trap

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
__maintainer__ = 'George Flanagin'
__email__ = ['gflanagin@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'

if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

@trap
def bytes_to_terabytes(bytes_value: int) -> float:
    """
    Convert bytes to terabytes (TB).

    Args:
    bytes_value (int): The value in bytes to convert.

    Returns:
    float: The value converted to terabytes.
    """
    terabytes = bytes_value / (1024 ** 4)  # 1 TB = 1024^4 bytes
    return terabytes

@trap
def get_user_disk_usage_with_quota(hostname:str, path: str) -> Tuple[str, Dict[str, float]]:
    """
    Get disk usage for each user in the specified path using xfs_quota.

    Args:
    hostname (str): The hostname of the machine.
    path (str): The directory path to analyze.

    Returns:
    tuple: A tuple containing the host name and a dictionary where keys are usernames and values are disk usage in terabytes.
    """
    # Construct the xfs_quota command
    command = f"sudo xfs_quota -x -c 'report -u -ah' {path}"

    # Execute the command and capture its output
    result=SloppyTree(dorunrun(""" ssh server "{command}" """, return_datatype=dict))
    if not result.OK:
        #
        #
    
        pass

    for line in result.stdout.split():
        user, space, _0, _1, _2, _3 = line.split()
        space = linuxutils.byte_size(space)

    return "Hog report generated successfully and stored in hog_report.db"

def get_user_disk_usage_without_quota(hostname: str, path: str) -> Tuple[str, Dict[str, float]]:
    """
    Get disk usage for each user in the specified path without using xfs_quota.

    Args:
    path (str): The directory path to analyze.

    Returns:
    tuple: A tuple containing the host name and a dictionary where keys are usernames and values are disk usage in terabytes.
    """
    user_disk_usage = {}

    # Iterate over each directory entry in the specified path
    for entry in os.scandir(path):
        if entry.is_dir():
            # Get the username from the directory name
            username = entry.name

            # Calculate the disk usage for the user's home directory
            user_home = os.path.join(path, username)
            try:
                disk_usage_bytes = shutil.disk_usage(user_home).used
                disk_usage_tb = bytes_to_terabytes(disk_usage_bytes)
                user_disk_usage[username] = disk_usage_tb
            except PermissionError:
                # Handle permission errors (e.g., unable to access user's home directory)
                user_disk_usage[username] = -1  # Set disk usage to -1 if unable to access

    return host_name, user_disk_usage


def is_xfs_filesystem(path):
    """
    Check if the specified path is on an XFS file system.
    """
    # Get the file system type of the specified path
    command = f"stat -f -c %T {path}"
    
    #result=SloopyTree(dorunrun(""" ssh server "{command}" """, return_datatype=dict))
    #if not result.OK
    #
    #
    #pass
    try:
        filesystem_type = subprocess.check_output(command, shell=True, text=True).strip()
        return filesystem_type == "xfs"
    except subprocess.CalledProcessError:
        # Error occurred while executing the command
        return False

def is_xfs_quota_installed():
    """
    Check if xfs_quota is installed on the system.
    """
    # Attempt to execute xfs_quota with a dummy command
    command = "xfs_quota -x -c 'help'"
    
    #result=SloopyTree(dorunrun(""" ssh server "{command}" """, return_datatype=dict))
    #if not result.OK
    #
    #
    #pass
    try:
        subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # xfs_quota is not installed or encountered an error
        return False

if __name__ == "__main__":
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Get disk usage for each user in the specified path.")
    parser.add_argument("hostname", type=str, help="The hostname of the machine.")
    parser.add_argument("path", type=str, help="The directory path to analyze.")

    # Parse command-line arguments
    args = parser.parse_args()

    # Get disk usage information
    hostname = args.hostname
    path = args.path

# Check if the specified path is on an XFS file system
    if is_xfs_filesystem(args.path):
        print("The specified path is on an XFS file system.")
    else:
        print("The specified path is not on an XFS file system.")

    # Check if xfs_quota is installed on the system
    if is_xfs_quota_installed():
        print("xfs_quota is installed on the system.")
    else:
        print("xfs_quota is not installed on the system.")

    # Check if quota is enabled for the specified path
    if is_xfs_filesystem(args.path):
        # Quota is enabled, use xfs_quota to get disk usage
        host_name, user_disk_usage = get_user_disk_usage_with_quota(args.hostname, args.path)
    else:
        # Quota is not enabled, use shutil.disk_usage to get disk usage
        host_name, user_disk_usage = get_user_disk_usage_without_quota(args.hostname, args.path)

    # Display disk usage information
    print(f"Host Name: {host_name}")
    for username, disk_usage_tb in user_disk_usage.items():
        print(f"User: {username}, Disk Usage: {disk_usage_tb:.3f} TB")

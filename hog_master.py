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
import re

###
# Installed libraries.
###

from    threshold_parser    import  parse_threshold_main    as  parse_threshold
from    threshold_parser    import  convert_threshold_main  as  convert_threshold
from    hogs_ext_report     import  hogs_ext_main           as  hogs_ext
from    hogs_xfs_report     import  hogs_xfs_main           as  hogs_xfs
from    check_filesystem    import  check_filesystem

###
# From hpclib
###
import linuxutils
from   urdecorators import trap

###
# imports and objects that are a part of this project
###
import sqlite3

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


@trap
def handler(signum:int, stack:object=None) -> None:
    """
    Map SIGHUP and SIGUSR1 to a restart/reload, and 
    SIGUSR2 and the other common signals to an orderly
    shutdown. 
    """
    global logger
    logger.debug("handler")
    global myconfig
    if signum in [ signal.SIGHUP, signal.SIGUSR1 ]: 
        dfstat_main(myconfig)

    elif signum in [ signal.SIGUSR2, signal.SIGQUIT, signal.SIGTERM, signal.SIGINT ]:
        logger.info(f'Closing up from signal {signum}')
        fileutils.fclose_all()
        sys.exit(os.EX_OK)

    else:
        return

# Function to create SQLite database and tables using SQL script file
@trap
def create_database_from_script(sql_file, server):
    # Connect to SQLite database (or create if it doesn't exist)
    try:    
        # Get the absolute path of the SQL script file
        script_path = os.path.join(os.path.dirname(__file__), sql_file)

        # Connect to SQLite database (or create if it doesn't exist)
        conn = sqlite3.connect('hog_reports.db')

        # Create a cursor object
        cursor = conn.cursor()

        # Read SQL script from file
        with open(script_path, 'r') as f:
            sql_script = f.read()

        # Execute SQL script
        cursor.executescript(sql_script)

        # Commit changes
        conn.commit()
    
        print(f"""
            
            #########################################################  
                Database and tables created successfully for {server}
            #########################################################
                """)
    
    except sqlite3.Error as e:
        print("Error executing SQL script:", e)
    finally:
        #Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@trap
# Function to insert data into SQLite database
def insert_hog_report(server, directory, user, quota_used_tb):
    
    # Connect to SQLite database
    conn = sqlite3.connect('hog_reports.db')

    # Create a cursor object
    cursor = conn.cursor()
    
    try:
        # Insert data into hog_reports table
        cursor.execute('''INSERT INTO hog_reports (server, directory, user, quota_used)
                      VALUES (?, ?, ?, ?)''', (server, directory, user, quota_used_tb))

        # Commit changes
        conn.commit()

        # Print confirmation message
        print("Inserted data into hog_reports table.")        
    
    except sqlite3.Error as e:
    # Rollback the transaction if an error occurs
        conn.rollback()
        
        # Print error message
        print("Error inserting data into hog_reports table:", e)
    
    # Close cursor and connection
    cursor.close()
    conn.close()

def hogMaster_main(servers:str, directory_path:str, threshold_tb:float) -> dict:
    # Loop through servers
    for server in servers:
        # Create database for each server
        create_database_from_script('hogs.sql', server)

       # Check filesystem type
        is_ext, filesystem_type_ext = check_filesystem(server, directory_path, r'ext\d')
        is_xfs, filesystem_type_xfs = check_filesystem(server, directory_path, r'xfs')

        # Display filesystem type and quota status
        if is_ext:
            print(f"Quota is enabled for {directory_path} on server {server} ({filesystem_type_ext} filesystem).")
            print("Results for hogs on ext:")
            quota_info = hogs_ext(server, directory_path)
            for user_data in quota_info:
                if float(user_data['quota_used_tb']) > threshold_tb:
                    insert_hog_report(server, directory_path, user_data['user'], user_data['quota_used_tb'])
        elif is_xfs:
            print(f"Quota is enabled for {directory_path} on server {server} ({filesystem_type_xfs} filesystem).")
            print("Results for hogs on xfs:")
            quota_info =  hogs_xfs(server, directory_path)  # Pass formatted_threshold_value here
            for user_data in quota_info:
                if float(user_data['quota_used_tb']) > threshold_tb:
                    insert_hog_report(server, directory_path, user_data['user'], user_data['quota_used_tb'])
        else:
            print(f"No quota enabled for {directory_path} on server {server}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="hogMaster_main", description="Check quota enablement for directories on different servers.")
    parser.add_argument("-s", "--servers", nargs="+", required=True, help="List of servers to connect to via SSH.")
    parser.add_argument("-d", "--directory_path", type=str, required=True, help="The path to the directory to check.")
    parser.add_argument("-th", "--threshold", type=str, required=True, help="The threshold to check.")

    args = parser.parse_args()

    # Parse the threshold string
    threshold_value, threshold_unit = parse_threshold(args.threshold)
    formatted_threshold_value = convert_threshold(threshold_value, threshold_unit)
    print(f"Formatted threshold: {formatted_threshold_value} Tb")

    # Call main function for each server with necessary arguments
    for server in args.servers:
        hogMaster_main([server], args.directory_path, formatted_threshold_value)

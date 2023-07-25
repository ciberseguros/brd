#!/usr/bin/env python3

import argparse
import logging
import os

# Parse command line arguments
try:
    parser = argparse.ArgumentParser(
                    prog='BRD Code Plagiarism Checker',
                    description='Compares code using symbolic standardization and winnowing hashes to detect plagiarism',
                    epilog='Use responsibly. Suspected plagiarists still deserve every human right. Have you been clear on your expectations?')

    parser.add_argument('input_directory', help="Perform an N^2 comparison among every file in this directory. To ignore certain file extensions, create a .brdignore file with a newline-separated list of things to ignore.")
    parser.add_argument('-r', '--recursive',
                    action='store_true', help="Compare all files in subdirectories of input_directory recursively. Note: Project structure comparison is not currently supported.")
    parser.add_argument('-c', '--cluster',
                    action='store_true', help="Cluster pairwise outputs into groups of similar files.")
    parser.add_argument('-v', '--verbose',
                    action='store_true', help="Show warning messages.")
    parser.add_argument('-vv', '--very-verbose',
                    action='store_true', help="Be very verbose, but not painfully so.")
    parser.add_argument('-d', '--debug',
                    action='store_true', help="Show every log message. May be painful.")
    parser.add_argument('-mf', '--max-filecount', default=1000, help="Set the max number of files to be compared. Default 1000 If raising this limit, remember this tool runs in n^2 time.")      
    parser.add_argument('-ms', '--max-size', default=100, help="Set the max size files to be compared in MB. Default 100. If raising this limit, watch out for RAM use and swapping causing slowdowns.") 

    args = parser.parse_args()
except Exception as err:
    print(f"Error parsing command line arguments: {type(err)}: {err}")
    exit(1)

# Initialize logger
try:
    brd_logger = logging.getLogger('brd_log')
    brd_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(log_formatter)

    if args.debug:
        console_handler.setLevel(logging.DEBUG)
        print("Log level set to DEBUG")
    elif args.very_verbose:
        console_handler.setLevel(logging.INFO)
    elif args.verbose:    
        console_handler.setLevel(logging.WARNING)
    else:
        console_handler.setLevel(logging.ERROR)

    
    brd_logger.addHandler(console_handler)

    brd_logger.info("BRD Logger Instantiated")

except Exception as err:
    print(f"Error setting up BRD logger: {type(err)}: {err}")
    exit(2)

# Validate command line parameters

try:

    # ensure input_dir is a directory
    if not os.path.exists(args.input_directory):
        brd_logger.error(f"Given input directory path does not exist: {args.input_directory}")
        exit(4)
    brd_logger.info("Given input_directory path exists")

    # ensure input_dir is a directory
    if not os.path.isdir(args.input_directory):
        brd_logger.error(f"Given input directory path is not a directory: {args.input_directory}")
        exit(5)
    brd_logger.info("Given input_directory path points to a directory")

    # ensure input_dir is non-empty

    # look for a .brdignore file
    brdignore_path = os.path.join(args.input_directory, ".brdignore")
    brdignore_exists = os.path.exists(brdignore_path)
    
    # if the .brdignore file exists, check that it is formatted correctly
    if brdignore_exists:
        brd_logger.info("Found a .brdignore file")

        brdignore_directives = []
        try:
            # load .brdignore if it exists, split by newlines, and ignore those file extensions
            with open(brdignore_path) as brdignore_file:
                brdignore_directives = sorted(list(set(list(a.strip() for a in brdignore_file.read().split("\n")))))
                if "" in brdignore_directives:
                    brdignore_directives.remove("")
                for brdignore_directive in brdignore_directives:
                    if "." != brdignore_directive[0]:
                        brd_logger.error(f"Unrecognized brdignore directive <<{brdignore_directive}>>. All directives must begin with .")
                        exit(9)
                brd_logger.debug(f"Ignoring the following file extensions: {brdignore_directives}")
        except Exception as err:
            brd_logger.error(f"Error opening .brdignore file at {brdignore_path}: {type(err)}: {err}")
            exit(8)

    # load every filepath within input_dir, excluding those forbidden by .brdignore
    list_of_files = []
    #TODO

    # check that the resultant list of paths is non-empty
    if len(list_of_files) == 0:
        msg = "List of files to compare is empty! "
        if not args.recursive:
            msg += f"Did you mean to specify a recursive discovery of files with the -r flag? "
        if brdignore_exists:
            msg += f"Is your .brdignore file too broad?"
        brd_logger.error(msg)
        exit(11)

    # fail if the list of paths contains too many files per the max-filecount
    if len(list_of_files) > args.max_filecount:
        brd_logger.error(f"List of files to compare is longer {len(list_of_files)} than the limit of {args.max_filecount} files")
        exit(12)

    # fail if input_dir contains file(s) larger than max-size


except Exception as err:
    brd_logger.error(f"Error testing given parameters: {type(err)}: {err}")
    exit(3)








#!/usr/bin/env python3

import argparse
import logging
import os
import brdignore
import brdanalyzer
import platform


# Parse command line arguments
try:
    parser = argparse.ArgumentParser(
                    prog='BRD Code Plagiarism Checker',
                    description='Compares code using symbolic standardization and winnowing hashes to detect plagiarism',
                    epilog='Use responsibly. Suspected plagiarists still deserve every human right. Have you been clear on your expectations?')

    parser.add_argument('input_directory', help="Perform an N^2 comparison among every file in this directory. To ignore certain file extensions, create a .brdignore file with a newline-separated list of wildcards to ignore.")
    
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
    
    parser.add_argument('-w', '--winnowing_hash_threshold',  default=brdanalyzer.WINNOWNING_DEFAULT_THRESHOLD,            
                        help=f"Overwrite the default winnowing test threshold of {brdanalyzer.WINNOWNING_DEFAULT_THRESHOLD}") 
    
    parser.add_argument('-t', '--tokenized_ngram_threshold', default=brdanalyzer.TOKENIZED_NGRAMS_TEST_DEFAULT_THRESHOLD, 
                        help=f"Overwrite the default tokenized Ngrams test threshold of {brdanalyzer.TOKENIZED_NGRAMS_TEST_DEFAULT_THRESHOLD}") 
    
    parser.add_argument('-s', '--whitespace_threshold',      default=brdanalyzer.WHITESPACE_GESTALT_DEFAULT_THRESHOLD,    
                        help=f"Overwrite the default whitespace gestalt test threshold of {brdanalyzer.WHITESPACE_GESTALT_DEFAULT_THRESHOLD}") 
    
    parser.add_argument('-o', '--outfile', default="brd_report.md", help="Tell BRD where to write its output report. BRD avoids ovewriting previous reports by adding an incremental counter.")      
    
    parser.add_argument('-k', '--clobber-prior-outfile',
                    action='store_true', help="overwrite any previous report file with the same outfile name.")

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

# Warn Windows users of compatibility issues
if platform.system() == "Windows":
    brd_logger.warn("BRD is not tested in Windows, and may behave unexpectedly.")

# Get list of files to compare

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
    if len(os.listdir(args.input_directory)) == 0:
        brd_logger.error(f"Given input directory exists, but is empty: {args.input_directory}")
        exit(6)
    brd_logger.info("Given input_directory path points to a non-empty directory")        

    # look for a .brdignore file
    brdignore_path = os.path.join(args.input_directory, ".brdignore")
    brdignore_exists = os.path.exists(brdignore_path)
    
    # if the .brdignore file exists, check that it is formatted correctly
    if brdignore_exists:
        brd_logger.info("Found a .brdignore file")
        brdign = brdignore.brdignorelist(brdignore_path)
        brd_logger.debug("Done loading brdignore")
    else:
        brd_logger.info(f"No .brdignore found")

    # load every filepath within input_dir
    if args.recursive:
        def load_contents(running_list, path):
            brd_logger.debug(f"Recursing through the directory {path}")
            for item in os.listdir(path):
                itempath = os.path.join(path, item)
                if os.path.isfile(itempath):
                    running_list.append(itempath)
                elif os.path.isdir(itempath):
                    load_contents(running_list, itempath)
        list_of_contents = []
        load_contents(list_of_contents, args.input_directory)
    else:
        list_of_contents = list(os.path.join(args.input_directory, a) for a in os.listdir(args.input_directory))

    # clean out every directory path
    list_of_files = []
    brd_logger.debug(f"Going through {len(list_of_contents)} paths to remove symlinks and directory paths.")
    for node in list_of_contents:
        if os.path.isfile(node) and not os.path.islink(node):
            if brdignore_exists:
                rule = brdign.ignore(node)
                if rule is None:
                    list_of_files.append(node)
                else:
                    brd_logger.debug(f"Removing path {node} because it matches a .brdignore directive: {rule}.")
            else:
                list_of_files.append(node)
        else:
            brd_logger.debug(f"Removing path {node} because it is not a file.")

        
    brd_logger.debug(f"Resultant list of files has length: {len(list_of_files)}")

    # check that the resultant list of paths is non-empty
    if len(list_of_files) == 0:
        msg = "List of files to compare is empty! "
        if not args.recursive:
            msg += f"Did you mean to specify a recursive discovery of files with the -r flag? "
        if brdignore_exists:
            msg += f"Is your .brdignore file too broad?"
        brd_logger.error(msg)
        exit(11)
    brd_logger.debug("List of files to compare is not empty")

    # fail if the list of paths contains too many files per the max-filecount
    if len(list_of_files) > args.max_filecount:
        brd_logger.error(f"List of files to compare is longer {len(list_of_files)} than the limit of {args.max_filecount} files")
        exit(12)
    brd_logger.debug(f"List of files to compare is not too long {len(list_of_files)}. Max file count is set to {args.max_filecount}")

    # fail if input_dir contains file(s) larger than max-size
    for file in list_of_files:
        filesize = (os.path.getsize(file) / 1000000)
        if filesize > args.max_size:
            brd_logger.error(f"An input file was found which was larger ({filesize}MB) than the max analysis size ({args.max_size}MB). You can set this limit with the -ms flag if you have the computational resources to handle larger files.")
            brd_logger.error(f"Large file path: {file}")
            exit(13)
    brd_logger.debug(f"List of files to compare does not contain a file too long to process. Max size is set to {args.max_size}MB")

except Exception as err:
    brd_logger.error(f"Error testing given parameters: {type(err)}: {err}")
    exit(3)

brd_logger.info(f"Successfully loaded list of input files to compare. Found {len(list_of_files)} files.")
for file in list_of_files:
    brd_logger.debug(f"{file}")

# Get outfile, and don't clobber the past
outfile_path = args.outfile

if not args.clobber_prior_outfile:
    while os.path.exists(outfile_path):
        outfile_path = f"yet_another_{outfile_path}"

# Do analysis

thresholds = {
            "Whitespace Gestalt Test"       : args.whitespace_threshold,
            "Tokenized Ngrams Test"         : args.tokenized_ngram_threshold,
            "Winnowing Hash Test"           : args.winnowing_hash_threshold
        }

brda = brdanalyzer.brdanalyzer(list_of_files, outfile_path, thresholds)
brd_logger.info("BRD Analyzer Engine initialized")

brda.do_whitespace_ngrams()
brd_logger.info("BRD Analyzer Engine whitespace ngrams test complete")

brda.do_tokenized_ngrams()
brd_logger.info("BRD Analyzer Engine tokenized ngrams test complete")

brda.do_winnowing_hash()
brd_logger.info("BRD Analyzer Engine winnowing hash test complete")

brda.write_report()

print("BRD Complete")
print(f"Report written to {outfile_path}.")

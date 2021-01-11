"""
Defines deployer main functionality.
"""

#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals
import argparse
import audioop
import math
import multiprocessing
import os
from json import JSONDecodeError
import subprocess
import sys
import tempfile
import wave
import json
import requests

def percentile(arr, percent):
    """
    Calculate the given percentile of arr.
    """
    arr = sorted(arr)
    index = (len(arr) - 1) * percent
    floor = math.floor(index)
    ceil = math.ceil(index)
    if floor == ceil:
        return arr[int(index)]
    
    try:  
        low_value = arr[int(floor)] * (ceil - index)
        high_value = arr[int(ceil)] * (index - floor)
    except Exception as ex:
        low_value = 0
        high_value = 0
    return low_value + high_value

class Deployer(object): # pylint: disable=too-few-public-methods
    """
    Class for converting a region of an input audio or video file into a FLAC audio file
    """
    def __init__(self, source_path):
        self.source_path = source_path

    def __call__(self, region):
            return None

def which(program):
    """
    Return the path for a given executable.
    """
    def is_exe(file_path):
        """
        Checks whether a file is executable.
        """
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)
    #necessary to run on Windows
    if os.name == "nt":
        program += ".exe"
    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        #looks for file in the script execution folder before checking on system path
        current_dir = os.getcwd()
        local_program = os.path.join(current_dir, program)
        if is_exe(local_program):
            return local_program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
    return None


def main():
    """
    Run deployer as a command-line program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('source_path', help="Path to the video or audio file to subtitle",
                        nargs='?')
    parser.add_argument('-o', '--output',
                        help="Output path for subtitles (by default, subtitles are saved in \
                        the same directory and name as the source path)")
    parser.add_argument('--list-formats', help="List all available subtitle formats",
                        action='store_true')
    parser.add_argument('--list-languages', help="List all available source/destination languages",
                        action='store_true')

    args = parser.parse_args()

    if args.list_formats:
        print("List of formats:")
        return 0

    if args.list_languages:
        print("List of languages:")
        return 0

    if not validate(args):
        return 1

def validate(args):
    """
    Check that the CLI arguments passed to autosub are valid.
    """
    if not args.source_path:
        print("Error: You need to specify a source path.")
        return False

    return True

if __name__ == '__main__':
    sys.exit(main())

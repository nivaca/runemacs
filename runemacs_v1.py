#!/usr/bin/env python3

# This script does the following:
# 1. If Emacs is already running, it loads the files given as arguments,
# or simply activates (focuses) the main window if no files are given.
# 2. If Emacs is not running, it runs it and
# loads the files given as arguments, if any.

# yay -S python-psutil xdotool

import psutil
import subprocess
import sys
import os
from shutil import which
import time


def checkIfProcessRunning(processName):
    ''' Check if there is any running process which
    contains the given name processName. '''
    # Iterate over the all the running process.
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied,
                psutil.ZombieProcess):
            pass
    return False


def getEmacsPID():
    ''' Returns emacs process ID. '''
    for proc in psutil.process_iter():
        if proc.name().lower() == "emacs":
            return proc.pid


def getEmacsWID(eid):
    ''' Returns emacs window ID.
    Since emacs may have serveral windows IDs,
    it only returns the last one of the list. '''
    result = subprocess.run(['xdotool', 'search', '--pid', f'{eid}'],
                            stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').split()[-1]


def runemacsclient(filename):
    ''' Runs emacs client with a single filename as argument. '''
    return subprocess.Popen(['emacsclient', '-a', 'emacs', '-n', filename],
                            stdout=subprocess.PIPE)


def runemacs(filename=''):
    ''' Runs emacs with a single filename as argument (which can be empty). '''
    if filename == '':
        return subprocess.Popen(['emacs'], stdout=subprocess.PIPE)
    else:
        return subprocess.Popen(['emacs', filename], stdout=subprocess.PIPE)


def main():
    # Check if xdotool is installed or in path
    if which('xdotool') is None:
        print('xdotool not installed. Exiting...')
        exit(0)

    num_args = len(sys.argv)

    inputfiles = []
    inputfile = ""
    emacsPID = 0
    emacsWID = 0

    emacsrunning = False
    inputfilegiven = False

    if checkIfProcessRunning("emacs"):
        emacsrunning = True
        emacsPID = getEmacsPID()
        emacsWID = getEmacsWID(emacsPID)

    if num_args > 1:
        inputfilegiven = True
        for i in range(1, num_args):
            inputfiles.append(sys.argv[(i)])

    # Emacs is already running
    if emacsrunning:
        # Case 1: Emacs is running and one or more files are given
        if inputfilegiven:
            for filename in inputfiles:
                result = runemacsclient(filename)

        # Case 2: Emacs is running but no files are given.
        # Just activate the window
        else:
            result = subprocess.Popen(['xdotool', 'windowactivate',
                                      f'{emacsWID}'], stdout=subprocess.PIPE)

    # Emacs is not already running
    else:
        # Case 3: Emacs is not running and one or many files are given
        if inputfilegiven:
            if len(inputfiles) == 1:
                runemacs(inputfiles[0])
            else:
                subprocess.Popen(['emacs'])
                time.sleep(3)
                # Wait until emacs completely loads.
                # This is necesary in order for emacs server to be loaded

                # and now load each of the files with emacsclient
                for filename in inputfiles:
                    result = runemacsclient(filename)

        # Case 4: Emacs is not running and no file is given
        else:
            result = runemacs()


if __name__ == '__main__':
    main()

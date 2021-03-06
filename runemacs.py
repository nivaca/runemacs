#!/usr/bin/env python3

# This script does the following:
# 1. If Emacs is already running, it loads the files given as arguments,
# or simply activates (focuses) the main window if no files are given.
# 2. If Emacs is not running, it runs it and
# loads the files given as arguments, if any.
# 3. Relocates Emacs' main window to occupy half of the screen.

# yay -S python-psutil xdotool

import subprocess
import sys
import time
from shutil import which
import psutil
from pprint import pprint as pp

WAITTIME = 3  # time to wait before loading file

def check_if_process_running(process_name: str) -> bool:
    """ Check if there is any running process which
    contains the given name processName. """
    # Iterate over the all the running process.
    processes = []
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied,
                psutil.ZombieProcess):
            pass
    if len(processes) > 0:
        return True
    else:
        return False


def get_emacs_pid() -> int:
    """ Returns emacs process ID. """
    for proc in psutil.process_iter():
        if proc.name().lower() == "emacs":
            return proc.pid


def get_emacs_wid(eid: int) -> str:
    """ Returns emacs window ID.
    Since emacs may have serveral windows IDs,
    it only returns the last one of the list. """
    result = subprocess.run(['xdotool', 'search', '--pid', f'{eid}'],
                            stdout=subprocess.PIPE)
    # pp(result.stdout.decode('utf-8'))
    # exit(0)
    if result.stdout.decode('utf-8') != '':
        return result.stdout.decode('utf-8').split()[-1]
    else:
        return ''


def run_emacs_client(filename: str):
    """ Runs emacs client with a single filename as argument. """
    return subprocess.Popen(['emacsclient', '-a', 'emacs', '-n', filename],
                            stdout=subprocess.PIPE)


def run_emacs(filename: str = ''):
    """ Runs emacs with a single filename as argument (which can be empty). """
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
    emacsrunning = False
    inputfilegiven = False

    if check_if_process_running("emacs"):
        emacsrunning = True
        emacs_pid = get_emacs_pid()
        emacs_wid = get_emacs_wid(emacs_pid)

    if num_args > 1:
        inputfilegiven = True
        for i in range(1, num_args):
            inputfiles.append(sys.argv[i])

    # Emacs is already running
    if emacsrunning:
        # Case 1: Emacs is running and one or more files are given
        if inputfilegiven:
            for filename in inputfiles:
                run_emacs_client(filename)

        # Case 2: Emacs is running but no files are given.
        # Just activate the window
        else:
            subprocess.Popen(['xdotool', 'windowactivate',
                              f'{emacs_wid}'], stdout=subprocess.PIPE)

    # Emacs is not running
    else:
        # Case 3: Emacs is not running and one or many files are given
        if inputfilegiven:
            subprocess.Popen(['emacs'])
            time.sleep(WAITTIME)
            # Wait until emacs completely loads.
            # This is necesary in order for emacs server to be loaded

            # and now load each of the files with emacsclient
            for filename in inputfiles:
                run_emacs_client(filename)

        # Case 4: Emacs is not running and no file is given
        else:
            run_emacs()

if __name__ == '__main__':
    main()

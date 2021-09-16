import psutil
import tkinter as tk
import subprocess
import re

# yay -S python-psutil xdotool tk


def get_curr_screen_geometry() -> str:
    """Workaround to get the size of the current screen in a multi-screen setup.
   Returns:
       geometry (str): The standard Tk geometry string.
           [width]x[height]+[left]+[top]
   From: https://stackoverflow.com/a/56913005/1815288
   """
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.destroy()
    return geometry


def relocate_emacs_window() -> bool:
    emacs_pid = get_emacs_pid()
    emacs_wid = get_emacs_wid(emacs_pid)
    subprocess.run(['xdotool', 'windowmove', emacs_wid, '0', '0'],
                   stdout=subprocess.PIPE)
    geometry = get_curr_screen_geometry()
    pattern = re.compile(r'(\d+)x(\d+).+')
    match = re.search(pattern, geometry)
    if match:
        width = match.group(1)
        height = match.group(2)
        width = str(int(width) / 2)
        subprocess.run(['xdotool', 'windowsize', emacs_wid, width, height],
                       stdout=subprocess.PIPE)
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
    return result.stdout.decode('utf-8').split()[-1]


def main():
    relocate_emacs_window()


if __name__ == '__main__':
    main()
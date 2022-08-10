#!/usr/local/bin/python3
from enum import Enum
import subprocess

class Rofi(Enum):
    SELECTED = 0
    CANCEL = 1

MAX_ROWS = 10
    

def rofi(prompt, options, rofi_args=[], fuzzy=True):
    optionstr = '\n'.join(option.replace('\n', ' ') for option in options)
    # args = ['rofi', '-sort', '-no-levenshtein-sort']
    # if fuzzy:
    #     args += ['-matching', 'fuzzy']
    # args += ['-dmenu', '-p', prompt, '-format', 's', '-i']
    # args += rofi_args
    # args = [str(arg) for arg in args]


    args = ['choose', '-m']
    # if fuzzy:
    #     args += ['-matching', 'fuzzy']
    # args += ['-dmenu', '-p', prompt, '-format', 's', '-i']
    # args += rofi_args
    # args = [str(arg) for arg in args]

    nrows = min(MAX_ROWS, len(options))
    args += ['-n', str(nrows)]
    # print(nrows)


    args += prompt

    result = subprocess.run(args, input=optionstr, stdout=subprocess.PIPE, universal_newlines=True)
    returncode = result.returncode
    selected = result.stdout.strip()

    try:
        index = [opt.strip() for opt in options].index(selected)
    except ValueError:
        index = -1

    if returncode == Rofi.SELECTED.value:
        returncode = Rofi.SELECTED
    elif returncode == Rofi.CANCEL.value:
        returncode = Rofi.CANCEL

    return returncode, index, selected

if __name__ == '__main__':
    print(rofi('test', ['a', 'b', 'c','a']))
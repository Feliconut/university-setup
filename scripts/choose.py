#!/usr/local/bin/python3
from enum import Enum
import subprocess

class Choose():
    class CODE(Enum):
        SELECTED = 0
        CANCEL = 1

    MAX_ROWS = 10
        
    @classmethod
    def run(cls, prompt, options, rofi_args=[], fuzzy=True):
        optionstr = '\n'.join(option.replace('\n', ' ') for option in options)
        # args = ['rofi', '-sort', '-no-levenshtein-sort']
        # if fuzzy:
        #     args += ['-matching', 'fuzzy']
        # args += ['-dmenu', '-p', prompt, '-format', 's', '-i']
        # args += rofi_args
        # args = [str(arg) for arg in args] 


        args = ['choose', '-m']
        args += ['-f','Cascadia Code PL']
        # if fuzzy:
        #     args += ['-matching', 'fuzzy']
        # args += ['-dmenu', '-p', prompt, '-format', 's', '-i']
        # args += rofi_args
        # args = [str(arg) for arg in args]

        nrows = min(cls.MAX_ROWS, len(options))
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

        if returncode == Choose.CODE.SELECTED.value:
            returncode = Choose.CODE.SELECTED
        elif returncode == Choose.CODE.CANCEL.value:
            returncode = Choose.CODE.CANCEL

        return returncode, index, selected

if __name__ == '__main__':
    print(Choose.run('test', ['a', 'b', 'c','a']))
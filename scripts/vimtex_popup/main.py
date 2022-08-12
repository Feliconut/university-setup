
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

import pyperclip

from .watch import watch

import shutil

def vimtex_popup(file_path:Path, file_callback, user_final_callback):

    subprocess.call([
        f"source ~/.zshrc; mvim --servername purdue --remote-silent \"{str(file_path)}\"",
    ], shell=True)

    sleep(1) # vim creates and deletes a swp file. so wait for it to finish.

    # use a mutable data type so only the pointer is passed to the callback
    file_content = [file_path.read_text()]

    def callback():
        if file_callback:
            del file_content[:]
            file_content.append(file_path.read_text())
            print(file_content[0])
            return file_callback(file_path, file_content[0])
 
    def final_callback():
        if user_final_callback:
            # shutil.rmtree(temp_path, ignore_errors=True)
            return user_final_callback(file_path, file_content[0])


    watch(file_path, callback, final_callback)

def clipboard_file_prefill(file_path:Path):
    file_path.write_text(pyperclip.paste())

def clipboard_file_callback(file_path,file_content):
    sleep(0.1)
    # print(file_path.read_text())
    # copy to clipboard

    pyperclip.copy(file_content)
    print(file_content)

def clipboard_final_callback(file_path, file_content):
    shutil.rmtree(file_path, ignore_errors=True)
    pyperclip.copy(file_content)
    print(file_content)


def wait_vim_edit(file_path: Path):
    do_exit = 0
    def final(*args):
        nonlocal do_exit
        do_exit = 1

    vimtex_popup(file_path, None, final)
    
    while not do_exit:
        sleep(0.1)
    





if __name__ == '__main__':
    temp_path = Path(r'/tmp/vimtex-popup')
    shutil.rmtree(temp_path, ignore_errors=True)
    Path.mkdir(temp_path, parents=True, exist_ok=True)
    # temp_path.touch()
    file_path = temp_path/'temp.tex'
    file_path.touch()
    clipboard_file_prefill(file_path)
    vimtex_popup(file_path, lambda x,y:None, clipboard_final_callback)






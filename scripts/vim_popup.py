#!/usr/local/bin/python3

from pathlib import Path
import shutil
from vimtex_popup import clipboard_file_callback, clipboard_final_callback, vimtex_popup, clipboard_file_prefill

temp_path = Path(r'/tmp/vimtex-popup')
shutil.rmtree(temp_path, ignore_errors=True)
Path.mkdir(temp_path, parents=True, exist_ok=True)
# temp_path.touch()
file_path = temp_path/'temp.tex'
file_path.touch()
clipboard_file_prefill(file_path)
vimtex_popup(file_path, lambda x,y:None, clipboard_final_callback)
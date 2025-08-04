import subprocess
import os
from config import iso_dump_folder, roms_folder, gc_fst_exe_path, input_iso_path, output_iso_path, root_path
import time


def extract_iso(exe_path = gc_fst_exe_path, 
                iso_path = input_iso_path,
                verbose=True):
    
    result = subprocess.run([exe_path, 'extract', iso_path], capture_output=True, text=True, errors="ignore")
    
    if verbose:
        print(result.stdout)
        print(result.stderr)

    return

def rebuild_iso(exe_path = gc_fst_exe_path, 
                root_path = root_path,
                output_iso_path = output_iso_path,
                verbose=True):

    result = subprocess.run([exe_path, 'rebuild', root_path, output_iso_path], capture_output=True, text=True,errors="ignore")

    if verbose:
        print(result.stdout)
        print(result.stderr)
    return


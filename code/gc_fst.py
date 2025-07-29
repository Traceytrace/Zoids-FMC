import subprocess
import os
from config import gc_fst_folder, roms_folder

gc_fst_exe_path = os.path.join(gc_fst_folder, 'gc_fst.exe')
input_iso_path = os.path.join(roms_folder, 'zoids.iso')
output_iso_path = os.path.join(roms_folder, 'zoids_edited.iso')
root_path = os.path.join(gc_fst_folder, 'root')

def extract_iso(exe_path = gc_fst_exe_path, 
                iso_path = input_iso_path,
                verbose=True):
    original_working_dir = os.path.dirname(os.getcwd())
    os.chdir(gc_fst_folder)
    result = subprocess.run([exe_path, 'extract', iso_path], capture_output=True, text=True,errors="ignore")
    os.chdir(original_working_dir)
    if verbose:
        print(result.stdout)
        print(result.stderr)
    return

def rebuild_iso(exe_path = gc_fst_exe_path, 
                root_path = root_path,
                output_iso_path = output_iso_path,
                verbose=True):
    original_working_dir = os.path.dirname(os.getcwd())
    os.chdir(gc_fst_folder)
    result = subprocess.run([exe_path, 'rebuild', root_path, output_iso_path], capture_output=True, text=True,errors="ignore")
    os.chdir(original_working_dir)
    if verbose:
        print(result.stdout)
        print(result.stderr)
    return


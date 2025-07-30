import os
import subprocess
from config import fpktool_path
fpktool_exe_path = os.path.join(fpktool_path, 'fpktool.exe')

def unpack_fpk(exe_path = fpktool_exe_path, 
                input_file = None,
                output_folder = None,
                verbose=True):
    
    result = subprocess.run([exe_path, '-u', input_file, output_folder], capture_output=True, text=True, errors="ignore")
    
    if verbose:
        print(result.stdout)
        print(result.stderr)
    return

def pack_fpk(exe_path = fpktool_exe_path,
             input_folder = None,
             output_file = None,
             verbose=True):
    
    result = subprocess.run([exe_path, '-p', input_folder, output_file], capture_output=True, text=True, errors="ignore")
    
    if verbose:
        print(result.stdout)
        print(result.stderr)
    return
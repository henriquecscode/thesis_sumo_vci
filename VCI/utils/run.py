import os
import subprocess
def run_subprocess(command, verbose=False):
    print("Running command: ", command)
    process=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if verbose:
        for line in process.stdout:
            print(line.decode().strip())
    if process.returncode != 0:
        raise Exception(f"Error running command: {command}")
    
def run_system(command):
    print("Running command: ", command)
    os.system(command)
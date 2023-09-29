import os
import shutil
import subprocess
from loggerpy.loggingMld import *

logger = Logger()
logger.set_level("info")

ROOT_PATH = os.path.join('..', 'mesh_data')
OUTPUT_PATH = os.path.join(ROOT_PATH, 'output')
LS_PATH = os.path.join(ROOT_PATH, 'study_meshes')

def empty_dir():
    """remove the content of OUTPUT_PATH"""
    for item in os.listdir(OUTPUT_PATH):
        item_path = os.path.join(OUTPUT_PATH, item)

        # Check if the item is a file
        if os.path.isfile(item_path):
            os.remove(item_path)  # Remove the file
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def perform_mesh_ls(path=LS_PATH):
    """perform a simple ls of the path parameter, extract the .mesh files return a list of files"""
    logger.debug("ls path : " + path)
    with subprocess.Popen(["ls", path], stderr = subprocess.PIPE, stdout=subprocess.PIPE, text=True) as ls_process:
        output, _ = ls_process.communicate()
        logger.debug("ls result : " + output)
        return [os.path.join(LS_PATH, file) for file in output.splitlines() if file.endswith(".mesh")]

def pretty_print_dic(dic):
    """pretty_print"""
    for key, value in dic.items():
        print(key)
        for elt in value:
            elt.pretty_print()
            print("\t-----------")
    print("=============")

import os
import subprocess
import sys
import json  # Changed from yaml to json
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.join(os.environ["MMGPLUGIN_ROOT_DIR"], "plugins", "mmgplugin"))
sys.path.append(os.path.join(os.environ["SMESH_ROOT_DIR"], "share", "salome", "plugins", "smesh"))

from myMmgPlugDialog import *


# Initialize QApplication
#app = QApplication(sys.argv)

result_dict = {}

ROOT_PATH = os.path.join(os.environ["MMGPLUGIN_ROOT_DIR"], "tests")
TWO_D_PATH = os.path.join(ROOT_PATH, '2D')


class Test:
    def __init__(self, filename, swap, insert, move, hausd, hgrad, hmin, hmax, choice, sandbox, default):
        self.filename = filename
        self.swap = swap
        self.insert = insert
        self.move = move
        self.hausd = hausd
        self.hgrad = hgrad
        self.hmin = hmin
        self.hmax = hmax
        self.choice = choice if choice else []
        self.sandbox = [{'left': '-' + elt['left'], 'right': elt['right']} for elt in sandbox] if sandbox else []
        self.default = default

def perform_ls(path=TWO_D_PATH):
    """Perform a simple ls of the path parameter, return a list of files"""
    with subprocess.Popen(["ls", path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as ls_process:
        output, _ = ls_process.communicate()
        return [os.path.join(path, file) for file in output.splitlines()]

def check_ok(mesh, test, mesh_type):
    if mesh.endswith('.sol') or mesh.endswith('_output.mesh'):
        return False
    dialog = MyMmgPlugDialog()

    # Fake PBMeshFilePressed without Qt interface
    ###
    dialog.LE_MeshFile.setText(mesh)
    dialog.fichierIn = str(mesh)
    dialog.currentName = os.path.splitext(os.path.basename(dialog.fichierIn))[0]
    dialog.MeshIn = ""
    dialog.LE_MeshSmesh.setText("")
    dialog.__selectedMesh = None
    dialog.isFile = True
    ###

    # Set all the parameters to be conform with the JSON
    ###
    if mesh_type == '2D':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMG2D'])
    else:
        return False

    dialog.CB_SwapEdge.setChecked(test.swap)
    dialog.CB_InsertEdge.setChecked(test.insert)
    dialog.CB_MoveEdge.setChecked(test.move)

    dialog.SP_Geomapp.setProperty("value", test.hausd)
    dialog.SP_Gradation.setProperty("value", test.hgrad)
    dialog.SP_Hmin.setProperty("value", test.hmin)
    dialog.SP_Hmax.setProperty("value", test.hmax)

    for elt in test.choice:
        if elt == 'auto':
            dialog.CB_RepairBeforeCompute.setChecked(True)
        elif elt == 'gen':
            dialog.CB_GenRepair.setChecked(True)
        elif elt == 'only':
            dialog.CB_RepairOnly.setChecked(True)

    for elt in test.sandbox:
        dialog.sandboxes[-1][0].setText(str(elt['left']))
        dialog.sandboxes[-1][1].setText(str(elt['right']))
        dialog.PBPlusPressed()

    if test.default:
        dialog.clean()
    ###

    # Compute Mesh
    ###
    result = dialog.PBOKPressed()
    ###

    if dialog.maFenetre is not None:
        dialog.maFenetre.theClose()

    # Close the dialog
    ###
    dialog.PBCancelPressed()
    ###

    result_dict[dialog.currentName] = result
    return result

def pretty_print():
    with open(os.path.join(ROOT_PATH, 'logs_2D.txt'), 'w') as f:
        for key, value in result_dict.items():
            f.write(key + ': ' + str(value) + '\n')

def main():
    # Load JSON data from a file
    with open(os.path.join(ROOT_PATH, 'testsuite_2D.json'), 'r') as file:
        data = json.load(file)

    print("\nstart 2D testing...\n")

    # Simplified the test iteration into a single loop
    for path, mesh_type in [(TWO_D_PATH, '2D')]:  # Combined all paths and types into a single loop
        ls = perform_ls(path)
        dict_tests = {}
        for item in data:
            for filepath in ls:
                if item['filename'] == os.path.basename(filepath):
                    dict_tests[filepath] = Test(**item)

        for mesh, test in dict_tests.items():
            check_ok(mesh, test, mesh_type)

    pretty_print()

main()


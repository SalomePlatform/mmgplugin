import os
import subprocess
import sys
import yaml

sys.path.append('/home/catB/ff275963/SALOME-9.11.0-native-UB22.04-SRC/BINARIES-UB22.04/SMESH/share/salome/plugins/smesh/mmgplugin/')
sys.path.append('/home/catB/ff275963/SALOME-9.11.0-native-UB22.04-SRC/BINARIES-UB22.04/SMESH/share/salome/plugins/smesh/')

from myMmgPlugDialog import *

result_dict = {}

ROOT_PATH = '/home/catB/ff275963/SALOME-9.11.0-native-UB22.04-SRC/BINARIES-UB22.04/SMESH/share/salome/plugins/smesh/mmgplugin/tests'
SURFACE_PATH = os.path.join(ROOT_PATH, 'surface')
THREE_D_PATH = os.path.join(ROOT_PATH, '3D')
TWO_D_PATH = os.path.join(ROOT_PATH, '2D')
GEN_PATH = os.path.join(ROOT_PATH, 'gen_surface')

class Test:
    def __init__(self, filename, swap, insert, move, hausd, hgrad, hmin, hmax, ar, choice, sandbox, default):
        self.filename = filename
        self.swap = swap
        self.insert = insert
        self.move = move
        self.hausd = hausd
        self.hgrad = hgrad
        self.hmin = hmin
        self.hmax = hmax
        self.ar = ar
        self.choice = choice
        self.sandbox = sandbox
        self.default = default
        if self.sandbox is None:
            self.sandbox = []
        if self.choice is None:
            self.choice = []

def perform_ls(path=SURFACE_PATH):
  """perform a simple ls of the path parameter, return a list of files"""
  with subprocess.Popen(["ls", path], stderr = subprocess.PIPE, stdout=subprocess.PIPE, text=True) as ls_process:
    output, _ = ls_process.communicate()
    return [os.path.join(path, file) for file in output.splitlines()]

def check_ok(mesh, test, mesh_type):
    if mesh.endswith('.sol') or mesh.endswith('_output.mesh'):
        return False
    dialog = MyMmgPlugDialog()

    # Fake PBMeshFilePressed without Qt interface
    ###
    dialog.LE_MeshFile.setText(mesh)
    dialog.fichierIn=str(mesh)
    dialog.currentName = os.path.splitext(os.path.basename(dialog.fichierIn))[0]
    dialog.MeshIn=""
    dialog.LE_MeshSmesh.setText("")
    dialog.__selectedMesh=None
    dialog.isFile = True
    ###

    # Set all the parameter to be conform with the yaml
    ###
    if mesh_type == 'surface':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMGS'])
    elif mesh_type == '2D':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMG2D'])
    elif mesh_type == '3D':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMG3D'])
    else:
        return False

    dialog.CB_SwapEdge.setChecked(test.swap)
    dialog.CB_InsertEdge.setChecked(test.insert)
    dialog.CB_MoveEdge.setChecked(test.move)

    dialog.SP_Geomapp.setProperty("value", test.hausd)
    dialog.SP_Ridge.setProperty("value", test.ar)
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
    test = dialog.PBOKPressed()
    ###

    if dialog.maFenetre is not None:
        dialog.maFenetre.theClose()

    # Close the dialog
    ###
    dialog.PBCancelPressed()
    ###

    result_dict[dialog.currentName] = test
    return test

def pretty_print():
    with open(os.path.join(ROOT_PATH, 'logs.txt'), 'w') as f:
        for key, value in result_dict.items():
            f.write(key + ': ' + str(value) + '\n')

def main():

    # Load YAML data from a file
    with open(os.path.join(ROOT_PATH, 'testsuite.yaml'), 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    print("start testing...")

    ls = perform_ls(SURFACE_PATH)
    dict_tests = {}
    for item in data:
        for path in ls:
            if item['filename'] == os.path.basename(path):
                dict_tests[path] = Test(**item)

    for mesh, test in dict_tests.items():
        check_ok(mesh, test, 'surface')

    ls = perform_ls(GEN_PATH)
    dict_tests = {}
    for item in data:
        for path in ls:
            if item['filename'] == os.path.basename(path):
                dict_tests[path] = Test(**item)

    for mesh, test in dict_tests.items():
        check_ok(mesh, test, 'surface')

    ls = perform_ls(THREE_D_PATH)
    dict_tests = {}
    for item in data:
        for path in ls:
            if item['filename'] == os.path.basename(path):
                dict_tests[path] = Test(**item)

    for mesh, test in dict_tests.items():
        check_ok(mesh, test, '3D')

    ls = perform_ls(TWO_D_PATH)
    dict_tests = {}
    for item in data:
        for path in ls:
            if item['filename'] == os.path.basename(path):
                dict_tests[path] = Test(**item)

    for mesh, test in dict_tests.items():
        check_ok(mesh, test, '2D')

    pretty_print()

main()

import os
import subprocess
import sys

sys.path.append('/home/catB/ff275963/SALOME-9.11.0-native-UB22.04-SRC/BINARIES-UB22.04/SMESH/share/salome/plugins/smesh/mmgplugin/')
sys.path.append('/home/catB/ff275963/SALOME-9.11.0-native-UB22.04-SRC/BINARIES-UB22.04/SMESH/share/salome/plugins/smesh/')

from myMmgPlugDialog import *

result_dict = {}

ROOT_PATH = '/home/catB/ff275963/SALOME-9.11.0-native-UB22.04-SRC/BINARIES-UB22.04/SMESH/share/salome/plugins/smesh/mmgplugin/tests'
SURFACE_PATH = os.path.join(ROOT_PATH, 'surface')
THREE_D_PATH = os.path.join(ROOT_PATH, '3D')
TWO_D_PATH = os.path.join(ROOT_PATH, '2D')

def perform_ls(path=SURFACE_PATH):
  """perform a simple ls of the path parameter, return a list of files"""
  with subprocess.Popen(["ls", path], stderr = subprocess.PIPE, stdout=subprocess.PIPE, text=True) as ls_process:
    output, _ = ls_process.communicate()
    return [os.path.join(path, file) for file in output.splitlines()]

def check_ok(mesh, mesh_type):
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

    if mesh_type == 'surface':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMGS'])
    elif mesh_type == '2D':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMG2D'])
    elif mesh_type == '3D':
        dialog.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMG3D'])
    else:
        return False

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
    print("start testing...")
    ls = perform_ls(SURFACE_PATH)
    for mesh in ls:
        check_ok(mesh, 'surface')

    ls = perform_ls(THREE_D_PATH)
    for mesh in ls:
        check_ok(mesh, '3D')

    ls = perform_ls(TWO_D_PATH)
    for mesh in ls:
        check_ok(mesh, '2D')

    pretty_print()

main()

if __name__ == '__main__':
    main()

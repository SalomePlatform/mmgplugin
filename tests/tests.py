import os
import subprocess

ROOT_PATH = '.'
SURFACE_PATH = os.path.join(ROOT_PATH, 'surface')
THREE_D_PATH = os.path.join(ROOT_PATH, '3D')
TWO_D_PATH = os.path.join(ROOT_PATH, '2D')

def perform_ls(path=SURFACE_PATH):
  """perform a simple ls of the path parameter, return a list of files"""
  with subprocess.Popen(["ls", path], stderr = subprocess.PIPE, stdout=subprocess.PIPE, text=True) as ls_process:
    output, _ = ls_process.communicate()
    return [os.path.join(path, file) for file in output.splitlines()]

def check_ok(mesh, mesh_type):
    pass

def main():
    ls = perform_ls(SURFACE_PATH)
    for mesh in ls:
        check_ok(mesh, 'surface')

    ls = perform_ls(THREE_D_PATH)
    for mesh in ls:
        check_ok(mesh, '3D')

    ls = perform_ls(TWO_D_PATH)
    for mesh in ls:
        check_ok(mesh, '2D')

if __name__ == '__main__':
    main()

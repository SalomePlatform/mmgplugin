import os
import tempfile
import salome
import subprocess

ROOT_PATH = '.'
LS_PATH = os.path.join(ROOT_PATH, 'archive_meshes')
OUTPUT_PATH = os.path.join(ROOT_PATH, 'study_meshes')

def start_salome():
    try:
        # Start Salome session
        salome.salome_init()
    except Exception as e:
        print(f"Error starting Salome: {str(e)}")
        raise

def quit_salome():
    try:
        # Close the current study and any modules
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser(1)
            salome.sg.closeServer(salome.myStudy)
    except Exception as e:
        print(f"Error closing Salome: {str(e)}")
        raise

def load_geometry(input_file):
    print(f'Loading {input_file}...')
    try:
        exec(compile(open(input_file, 'rb').read(), input_file, 'exec'))

        import SMESH
        from salome.smesh import smeshBuilder
        smesh = smeshBuilder.New()

        study = salome.myStudy
        smesh.UpdateStudy()
        name = os.path.splitext(os.path.basename(input_file))[0]
        SO = study.FindObjectByName(name, 'SMESH')[0]
        mesh = smesh.Mesh(SO.GetObject(), name)

        return mesh
    except Exception as e:
        print(f"Error loading geometry: {str(e)}")
        raise

def export_mesh(mesh, mesh_file):
    print(f'Exporting the mesh from {mesh_file}...')
    try:
        mesh.ExportGMF(mesh_file)

    except Exception as e:
        print(f"Error exporting the mesh: {str(e)}")
        raise

def perform_py_ls(path=LS_PATH):
    """perform a simple ls of the path parameter, extract the .py files return a list of files"""
    with subprocess.Popen(["ls", path], stderr = subprocess.PIPE, stdout=subprocess.PIPE, text=True) as ls_process:
        output, _ = ls_process.communicate()
        return [os.path.join(LS_PATH, file) for file in output.splitlines() if file.endswith(".py")]

def create_mesh_file(input_file, output_dir):
    # Start Salome session
    start_salome()

    # Load the geometry from the input file
    mesh = load_geometry(input_file)

    # Perform necessary operations to create the mesh
    # Modify this part to suit your specific meshing requirements

    # Save the mesh to a temporary file
    temp_mesh_file = os.path.join(output_dir, os.path.basename(os.path.splitext(input_file)[0] + '.mesh'))
    export_mesh(mesh, temp_mesh_file)

    # Quit Salome session
    quit_salome()

    return temp_mesh_file

def main():
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for input_file in perform_py_ls():
        mesh_file = create_mesh_file(input_file, OUTPUT_PATH)
        print(f"Mesh file generated: {mesh_file}")
        print('----------------')


if __name__ == "__main__":
    main()


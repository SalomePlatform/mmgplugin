# Study of the MMGS parameters influence on different meshes

The objective
========

The objective is to understand how to make automatic the selection of the values of the MMG parameters depending of some mesh informations.

How to
========

* To run the application, launch the following commands:
>  cd src;
>  ./launch.sh
* Select the meshes you want to study and add them to the directory `mesh_data/study_meshes`. You can store meshes in `mesh_data/archive_meshes`
* Find already generated meshes in `mesh_data/archive_meshes`. They are stored as SALOME studies. Generate the .mesh files with the following commands:
> cd mesh_data;
> [path-to-your-SALOME-binary] shell -l -script MakeMesh.py
* Select the functions you want to compute in `src/main.py`
* Find all the generated images in `studies`

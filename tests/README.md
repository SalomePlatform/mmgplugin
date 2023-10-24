# Tests for the MMG plugin

How to: misc
========

* You can add volume meshes to the `3D` directory, surface meshes to the `surface` directory, and 2D meshes to the 2D directory.
* Generate surface meshes in the `gen_surface` directory with the following command:
> make
* Delete them with the following command:
> make clean

How to: testsuite
========

To run the testsuite:
1. Generate the additional meshes (optional):
>  make;
2. Start SALOME
> $SALOME_ROOT_DIR/salome
3. Start SMESH and load the script `tests.py` of this directory
4. The results are stored in a generated file `logs.txt` in this directory.

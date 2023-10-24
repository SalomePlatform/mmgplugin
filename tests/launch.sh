#!/bin/sh
mkdir -p gen_surface
mkdir -p surface
mkdir -p 3D
mkdir -p 2D

~/SALOME-9.11.0-native-UB22.04-SRC/salome shell -l -script MakeMesh.py
python3 tests.py

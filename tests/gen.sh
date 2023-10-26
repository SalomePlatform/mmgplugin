#!/bin/sh
mkdir -p gen_surface
mkdir -p surface
mkdir -p 3D
mkdir -p 2D

cd ../misc/mesh_data
make
cd ../../tests
cp ../misc/mesh_data/archive_meshes/*.mesh gen_surface

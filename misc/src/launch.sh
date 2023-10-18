#!/bin/sh
mkdir -p ../mesh_data/output
mkdir -p ../studies/hausd_hgrad/contour
mkdir -p ../studies/hausd_hgrad/surface

mkdir -p ../studies/hmin_hmax/contour
mkdir -p ../studies/hmin_hmax/surface

mkdir -p ../studies/hmin_hmax_hgrad/contour
mkdir -p ../studies/hmin_hmax_hgrad/surface

mkdir -p ../studies/hmin_hmax_hausd/contour
mkdir -p ../studies/hmin_hmax_hausd/surface

mkdir -p ../studies/hausd_box/contour
mkdir -p ../studies/hausd_box/surface

mkdir -p ../studies/hsiz_box/contour
mkdir -p ../studies/hsiz_box/surface

mkdir -p ../studies/hausd_hsiz/contour
mkdir -p ../studies/hausd_hsiz/surface

python3 main.py

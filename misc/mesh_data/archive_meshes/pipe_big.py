#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.11.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, f'{os.environ["PWD"]}/archive_meshes')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
[PipeTShape_1, Junction_1, Junction_2, Junction_3, Thickness, Circular_quarter_of_pipe, Circular_quarter_of_pipe_1, Main_pipe_half_length, Flange, Incident_pipe_half_length, Internal_faces] = geompy.MakePipeTShape(70, 10, 160, 40, 10, 180, True)
[geomObj_1, geomObj_2, geomObj_3, geomObj_4, geomObj_5, geomObj_6, geomObj_7, geomObj_8, geomObj_9, Junction_1, Junction_2, Junction_3, Thickness, Circular_quarter_of_pipe, Circular_quarter_of_pipe_1, geomObj_10, geomObj_11, Main_pipe_half_length, Flange, Incident_pipe_half_length, geomObj_12, geomObj_13, geomObj_14, Internal_faces] = geompy.GetExistingSubObjects(PipeTShape_1, False)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( PipeTShape_1, 'PipeTShape_1' )
geompy.addToStudyInFather( PipeTShape_1, Junction_1, 'Junction 1' )
geompy.addToStudyInFather( PipeTShape_1, Junction_2, 'Junction 2' )
geompy.addToStudyInFather( PipeTShape_1, Junction_3, 'Junction 3' )
geompy.addToStudyInFather( PipeTShape_1, Thickness, 'Thickness' )
geompy.addToStudyInFather( PipeTShape_1, Circular_quarter_of_pipe, 'Circular quarter of pipe' )
geompy.addToStudyInFather( PipeTShape_1, Circular_quarter_of_pipe_1, 'Circular quarter of pipe' )
geompy.addToStudyInFather( PipeTShape_1, Main_pipe_half_length, 'Main pipe half length' )
geompy.addToStudyInFather( PipeTShape_1, Flange, 'Flange' )
geompy.addToStudyInFather( PipeTShape_1, Incident_pipe_half_length, 'Incident pipe half length' )
geompy.addToStudyInFather( PipeTShape_1, Internal_faces, 'Internal faces' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

pipe_big = smesh.Mesh(PipeTShape_1,'pipe_big')
NETGEN_1D_2D_3D = pipe_big.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
NETGEN_3D_Parameters_1 = NETGEN_1D_2D_3D.Parameters()
NETGEN_3D_Parameters_1.SetMaxSize( 44.2267 )
NETGEN_3D_Parameters_1.SetMinSize( 3.28477 )
NETGEN_3D_Parameters_1.SetSecondOrder( 0 )
NETGEN_3D_Parameters_1.SetOptimize( 1 )
NETGEN_3D_Parameters_1.SetFineness( 2 )
NETGEN_3D_Parameters_1.SetChordalError( -1 )
NETGEN_3D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_3D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_3D_Parameters_1.SetFuseEdges( 1 )
NETGEN_3D_Parameters_1.SetQuadAllowed( 0 )
NETGEN_3D_Parameters_1.SetCheckChartBoundary( 3 )
Junction_1_1 = pipe_big.GroupOnGeom(Junction_1,'Junction 1',SMESH.FACE)
Junction_2_1 = pipe_big.GroupOnGeom(Junction_2,'Junction 2',SMESH.FACE)
Junction_3_1 = pipe_big.GroupOnGeom(Junction_3,'Junction 3',SMESH.FACE)
Thickness_1 = pipe_big.GroupOnGeom(Thickness,'Thickness',SMESH.EDGE)
Circular_quarter_of_pipe_2 = pipe_big.GroupOnGeom(Circular_quarter_of_pipe,'Circular quarter of pipe',SMESH.EDGE)
Circular_quarter_of_pipe_3 = pipe_big.GroupOnGeom(Circular_quarter_of_pipe_1,'Circular quarter of pipe',SMESH.EDGE)
Main_pipe_half_length_1 = pipe_big.GroupOnGeom(Main_pipe_half_length,'Main pipe half length',SMESH.EDGE)
Flange_1 = pipe_big.GroupOnGeom(Flange,'Flange',SMESH.EDGE)
Incident_pipe_half_length_1 = pipe_big.GroupOnGeom(Incident_pipe_half_length,'Incident pipe half length',SMESH.EDGE)
Internal_faces_1 = pipe_big.GroupOnGeom(Internal_faces,'Internal faces',SMESH.FACE)
isDone = pipe_big.Compute()
[ Junction_1_1, Junction_2_1, Junction_3_1, Thickness_1, Circular_quarter_of_pipe_2, Circular_quarter_of_pipe_3, Main_pipe_half_length_1, Flange_1, Incident_pipe_half_length_1, Internal_faces_1 ] = pipe_big.GetGroups()


## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D_3D.GetAlgorithm(), 'NETGEN 1D-2D-3D')
smesh.SetName(NETGEN_3D_Parameters_1, 'NETGEN 3D Parameters_1')
smesh.SetName(Junction_1_1, 'Junction 1')
smesh.SetName(Junction_2_1, 'Junction 2')
smesh.SetName(Junction_3_1, 'Junction 3')
smesh.SetName(Internal_faces_1, 'Internal faces')
smesh.SetName(pipe_big.GetMesh(), 'pipe_big')
smesh.SetName(Thickness_1, 'Thickness')
smesh.SetName(Circular_quarter_of_pipe_3, 'Circular quarter of pipe')
smesh.SetName(Circular_quarter_of_pipe_2, 'Circular quarter of pipe')
smesh.SetName(Flange_1, 'Flange')
smesh.SetName(Main_pipe_half_length_1, 'Main pipe half length')
smesh.SetName(Incident_pipe_half_length_1, 'Incident pipe half length')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()

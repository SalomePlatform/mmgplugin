# -*- coding: utf-8 -*-
# Copyright (C) 2023-2024"  CEA/DES, EDF R&D
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#

import SMESH
import salome
import os
from salome.smesh import smeshBuilder
from math import *

class Values():
  def __init__(self, MeshName, num, currentName=""):
    self.geomapp = 0.01
    self.hmin = 0.01
    self.hmax = 10
    self.hgrad = 1.3
    self.MeshName = MeshName
    if currentName != "":
      self.CpyName = currentName + '_Repaired_' + str(num)
    else:
      self.CpyName = os.path.basename(os.path.splitext(MeshName)[0]) + '_Repaired_' + str(num)
    salome.salome_init()
    self.study = salome.myStudy
    self.smesh_builder = smeshBuilder.New()
    self.smesh_builder.UpdateStudy()
    self.CpyMesh = None
    if (len(self.study.FindObjectByName(self.MeshName, 'SMESH')) > 0):
      self.SelectedObject = self.study.FindObjectByName(self.MeshName, 'SMESH')[-1]
    else:
      self.SelectedObject = None
      FullMesh = self.smesh_builder.CreateMeshesFromMED(self.MeshName)[0] #TODO error handling (self.MyMesh[1].code, self.MyMesh[1].hasBadMesh)
      self.CpyMesh = FullMesh[0]
      self.CpyMesh.SetName(self.CpyName)
    if (self.CpyMesh is None) and (self.SelectedObject is not None):
      self.CpyMesh = self.smesh_builder.CopyMesh(self.SelectedObject.GetObject(), self.CpyName, True, True)

    self.bb = self.CpyMesh.GetBoundingBox()
    self.diag = sqrt((self.bb.maxX - self.bb.minX)**2 + (self.bb.maxY - self.bb.minY)**2 + (self.bb.maxZ - self.bb.minZ)**2)

    self.min_length = 0
    self.AvgAspects = 0

    self.FreeNodes = []
    self.FreeBorders = []
    self.FreeEdges = []

    self.CoincidentNodes = []

    self.DoubleNodes = []
    self.DoubleEdges = []
    self.DoubleFaces = []

  def GetInfoFromFilter(self, ElementType, FilterName):
    aFilter = self.smesh_builder.GetFilter(ElementType, FilterName)
    return self.CpyMesh.GetIdsFromFilter(aFilter)

  def FillInfos(self):
    # Get the faces aspect ratios
    faces = self.CpyMesh.GetElementsByType(SMESH.FACE)
    aspects = [self.CpyMesh.GetAspectRatio(id) for id in faces]
    self.avg_aspects = sum(aspects) / len(aspects) 
    
    # Get infos about free elements
    self.FreeNodes = self.GetInfoFromFilter(SMESH.NODE, SMESH.FT_FreeNodes)
    self.FreeBorders = self.GetInfoFromFilter(SMESH.EDGE, SMESH.FT_FreeBorders)
    self.FreeEdges = self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_FreeEdges)


    self.DoubleNodes = self.GetInfoFromFilter(SMESH.NODE, SMESH.FT_EqualNodes)
    self.DoubleEgdes = self.GetInfoFromFilter(SMESH.EDGE, SMESH.FT_EqualEdges)
    self.DoubleFaces = self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_EqualFaces)
    if self.DoubleFaces != [] or self.DoubleEgdes != [] or self.DoubleNodes != []:
      # Get minimal length (approx)
      start_treshold = self.diag / 100
      treshold = start_treshold
      step = start_treshold
      self.min_length = treshold
      edges = []
      while True:
        if len(edges) == 1:
          break
        edges = []
        while len(edges) == 0:
          LengthFilter = self.smesh_builder.GetFilter(SMESH.FACE, SMESH.FT_Length2D, SMESH.FT_LessThan, treshold)
          edges = self.CpyMesh.GetIdsFromFilter(LengthFilter)
          treshold += step
        self.min_length = treshold
        if step < treshold/1000:
          break
        step /= 1.5
        treshold = start_treshold

    self.CoincidentNodes = self.CpyMesh.FindCoincidentNodesOnPart([self.CpyMesh], self.min_length/1000, [], 0)
    # Get infos about double elements
    self.DoubleNodes = self.GetInfoFromFilter(SMESH.NODE, SMESH.FT_EqualNodes)
    self.DoubleEgdes = self.GetInfoFromFilter(SMESH.EDGE, SMESH.FT_EqualEdges)
    self.DoubleFaces = self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_EqualFaces)

  def ComputeNewDefaultValues(self):
    self.hmin = (self.diag * 0.01) / 17.25 # Reproduce default MMG values
    self.hmax = (self.diag * 2) / 1.723  # Reproduce default MMG values


  def AnalysisAndRepair(self, GenRepair):
    self.FillInfos()

    if len(self.FreeEdges) != 0:
      self.CpyMesh.RemoveElements(self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_FreeEdges))
    if len(self.FreeBorders) != 0:
      self.CpyMesh.RemoveElements(self.GetInfoFromFilter(SMESH.EDGE, SMESH.FT_FreeBorders))
    if len(self.FreeNodes) != 0:
      self.CpyMesh.RemoveOrphanNodes()
    
    if len(self.CoincidentNodes) != 0:
      self.CpyMesh.MergeNodes(self.CoincidentNodes, AvoidMakingHoles=True)

    tolerance = self.min_length/10
    while len(self.DoubleFaces) != 0:
      self.CoincidentNodes = self.CpyMesh.FindCoincidentNodesOnPart([self.CpyMesh], tolerance, [], 0)
      self.CpyMesh.MergeNodes(self.CoincidentNodes, AvoidMakingHoles=True)
      EqualElements = self.CpyMesh.FindEqualElements()
      self.CpyMesh.MergeElements(EqualElements)
      self.DoubleFaces = self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_EqualFaces)
      tolerance += self.min_length/100

    self.FillInfos()
    if GenRepair:
      self.CpyMesh.Compute()
      self.smesh_builder.UpdateStudy()
    if salome.sg.hasDesktop() and GenRepair and not self.CpyName.endswith('_0'):
      salome.sg.updateObjBrowser()

  def DeleteMesh(self):
    if self.CpyMesh is not None:
      self.smesh_builder.RemoveMesh(self.CpyMesh)
      self.CpyMesh = None
      if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()


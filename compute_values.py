import SMESH
import salome
import os
import sys
from salome.smesh import smeshBuilder
from math import *

class Values():
    def __init__(self, MeshName, num):
        self.geomapp = 0.01
        self.ridge = 45
        self.hmin = 0.01
        self.hmax = 10
        self.hgrad = 1.3
        self.MeshName = MeshName
        self.CpyName = os.path.basename(os.path.splitext(MeshName)[0]) + '_Repaired_' + str(num)
        salome.salome_init()
        study = salome.myStudy
        self.smesh_builder = smeshBuilder.New()
        self.smesh_builder.UpdateStudy()
        self.CpyMesh = None
        sys.stderr.write(MeshName + "  " + self.CpyName + "\n")
        if (len(study.FindObjectByName(self.MeshName, 'SMESH')) > 0):
            self.SelectedObject = study.FindObjectByName(self.MeshName, 'SMESH')[-1]
        else:
            self.SelectedObject = None
            FullMesh = self.smesh_builder.CreateMeshesFromGMF(self.MeshName) #TODO error handling (self.MyMesh[1].code, self.MyMesh[1].hasBadMesh)
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
            #sef.CpyMesh.RemoveNodes(self.GetInfoFromFilter(SMESH.NODE, SMESH.FT_FreeNodes))
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
            with open(os.path.join(os.path.expanduser('~'), 'logs.txt'), 'a') as f:
                f.write(str(tolerance) + '   ' + str(self.DoubleFaces) + '\n')
            tolerance += self.min_length/100

        self.FillInfos()
        self.CpyMesh.Compute()
        self.smesh_builder.UpdateStudy()
        if salome.sg.hasDesktop() and GenRepair and not self.CpyName.endswith('_0'):
          sys.stderr.write("update browser\n")
          salome.sg.updateObjBrowser()

    def DeleteMesh(self):
        if self.CpyMesh is not None:
            self.smesh_builder.RemoveMesh(self.CpyMesh)
            self.CpyMesh = None
            if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()


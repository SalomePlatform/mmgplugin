import SMESH
import salome
import os
from salome.smesh import smeshBuilder

class Values():
    def __init__(self, MeshName, num):
        self.geomapp = 0.01
        self.ridge = 45
        self.hsize = 0.1
        self.hgrad = 1.3
        self.MeshName = MeshName
        self.CpyName = os.path.basename(os.path.splitext(MeshName)[0]) + '_Repaired_' + str(num)
        salome.salome_init()
        study = salome.myStudy
        self.smesh_builder = smeshBuilder.New()
        self.smesh_builder.UpdateStudy()
        if (len(study.FindObjectByName(self.MeshName, 'SMESH')) > 0):
            self.SelectedObject = study.FindObjectByName(self.MeshName, 'SMESH')[-1]
            self.CpyMesh = None
        else:
            self.SelectedObject = None
            self.CpyMesh = self.smesh_builder.CreateMeshesFromGMF(MeshName)[0] #TODO error handling (self.MyMesh[1].code, self.MyMesh[1].hasBadMesh)
            self.CpyMesh.SetName(self.CpyName)

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

        """
        LengthFilter = self.smesh_builder.GetFilter(SMESH.FACE, SMESH.FT_Length2D, SMESH.FT_MoreThan, 0) # All lengths
        self.edges = self.CpyMesh.GetIds
        """
        self.CoincidentNodes = self.CpyMesh.FindCoincidentNodesOnPart([self.CpyMesh], 1e-05, [], 0)
        # Get infos about double elements
        self.DoubleNodes = self.GetInfoFromFilter(SMESH.NODE, SMESH.FT_EqualNodes)
        self.DoubleEgdes = self.GetInfoFromFilter(SMESH.EDGE, SMESH.FT_EqualEdges)
        self.DoubleFaces = self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_EqualFaces)

    def ComputeNewDefaultValues(self):
        pass

    def AnalysisAndRepair(self):
        if (self.CpyMesh is None) and (self.SelectedObject is not None):
            self.CpyMesh = self.smesh_builder.CopyMesh(self.SelectedObject.GetObject(), self.CpyName, True, True)
        self.FillInfos()

        if len(self.FreeEdges) != 0:
            self.CpyMesh.RemoveElements(self.GetInfoFromFilter(SMESH.FACE, SMESH.FT_FreeEdges))
        if len(self.FreeBorders) != 0:
            self.CpyMesh.RemoveElements(self.GetInfoFromFilter(SMESH.EDGE, SMESH.FT_FreeBorders))
        if len(self.FreeNodes) != 0:
            #sef.CpyMesh.RemoveNodes(self.GetInfoFromFilter(SMESH.NODE, SMESH.FT_FreeNodes))
            self.CpyMesh.RemoveOrphanNodes()
        
        if len(self.CoincidentNodes) != 0:
            self.CpyMesh.MergeNodes(self.CoincidentNodes)

        #TODO Remove the double faces by increasing treshold and merging elements

        self.FillInfos()
        self.CpyMesh.Compute()
        self.smesh_builder.UpdateStudy()
        if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()

    def DeleteMesh(self):
        if self.CpyMesh is not None:
            self.smesh_builder.RemoveMesh(self.CpyMesh)
        if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()


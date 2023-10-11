import SMESH
import salome
from salome.smesh import smeshBuilder

class Values():
    def __init__(self, MeshName):
        self.geomapp = 0.01
        self.ridge = 45
        self.hsize = 0.1
        self.hgrad = 1.3
        self.MeshName = MeshName
        salome.salome_init()
        study = salome.myStudy
        self.SelectedObject = study.FindObjectByName(self.MeshName, 'SMESH')[0]
        self.smesh_builder = smeshBuilder.New()
        self.MyMesh = self.smesh_builder.Mesh(self.SelectedObject.GetObject(), self.MeshName)
        self.MyMesh.Compute()
        self.CpyMesh = None
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
        return self.MyMesh.GetIdsFromFilter(aFilter)

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
        self.CpyMesh = self.smesh_builder.CopyMesh(self.SelectedObject.GetObject(), 'StatMesh', True, True)
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
        self.FillInfos()
        self.smesh_builder.UpdateStudy()

    def DeleteMesh(self):
        if self.CpyMesh is not None:
            self.smesh_builder.RemoveMesh(self.CpyMesh)


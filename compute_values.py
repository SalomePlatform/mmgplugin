class Values():
    def __init__(self, Meshname):
        self.geomapp = 0.01
        self.ridge = 45
        self.hsize = 0.1
        self.hgrad = 1.3
        self.MeshName = Meshname
        import SMESH
        from salome import salome_init_without_session
        from salome.smesh import smeshBuilder
        salome.salome_init_without_session()
        study = salome.myStudy
        SelectedObject = study.FindObjectByName(self.Meshname, 'SMESH')[0]
        smesh_builder = smeshBuilder.New()
        self.MyMesh = smesh_builder.Mesh(SelectedObject.GetObject(), 'StatMesh')
        self.AvgAspects = 0

        self.FreeNodes = []
        self.FreeBorders = []
        self.FreeEdges = []
        self.FreeFaces = []

        self.DoubleNodes = []
        self.DoubleEdges = []
        self.DoubleFaces = []

    def GetInfoFromFilter(self, ElementType, FilterName):
        aFilter = smesh_builder.GetFilter(ElementType, FilterName)
        return self.MyMesh.GetIdsFromFilter(aFilter)

    def FillInfos(self):
        # Get the faces aspect ratios
        faces = self.MyMesh.GetElementsByType(SMESH.FACE)
        aspects = [self.MyMesh.GetAspectRatio(id) for id in faces]
        self.avg_aspects = sum(aspects) / len(aspects) 
        
        # Get infos about free elements
        self.FreeNodes = GetInfoFromFilter(SMESH.NODE, SMESH.FT_FreeNodes)
        self.FreeBorders = GetInfoFromFilter(SMESH.EDGE, SMESH.FT_FreeBorders)
        self.FreeEdges = GetInfoFromFilter(SMESH.FACE, SMESH.FT_FreeEdges)
        self.FreeFaces = GetInfoFromFilter(SMESH.FACE, SMESH.FT_FreeFaces)

        # Get infos about double elements
        self.DoubleNodes = GetInfoFromFilter(SMESH.NODE, SMESH.FT_EqualNodes)
        self.DoubleEgdes = GetInfoFromFilter(SMESH.EDGE, SMESH.FT_EqualEdges)
        self.DoubleFaces = GetInfoFromFilter(SMESH.FACE, SMESH.FT_EqualFaces)

    def ComputeNewDefaultValues(self):
        pass

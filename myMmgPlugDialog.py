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

# Modules Python
# Modules Eficas

import os, subprocess
import tempfile
import re
import sys
import platform
from mmgplugin.MyPlugDialog_ui import Ui_MyPlugDialog
from mmgplugin.myViewText import MyViewText
from qtsalome import *
from mmgplugin.compute_values import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

verbose = True

REMESHER_DICT = { 'MMGS' : 0, 'MMG2D' : 1, 'MMG3D' : 2 }

class MyMmgPlugDialog(Ui_MyPlugDialog,QWidget):
  """
  """
  def __init__(self):
    QWidget.__init__(self)
    self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    self.setupUi(self)
    self.connecterSignaux()
    self.fichierIn=""
    self.fichierOut=""
    self.MeshIn=""
    self.commande=""
    self.num=1
    self.numRepair=1
    self.__selectedMesh=None
    self.values = None
    self.isFile = False
    self.currentName = ""

    # complex with QResources: not used
    # The icon are supposed to be located in the $SMESH_ROOT_DIR/share/salome/resources/smesh folder,
    # other solution could be in the same folder than this python module file:
    # iconfolder=os.path.dirname(os.path.abspath(__file__))

    self.iconfolder=os.path.join(os.environ["SMESH_ROOT_DIR"], "share", "salome", "resources", "smesh")
    icon = QIcon()
    icon.addFile(os.path.join(self.iconfolder,"select1.png"))
    self.PB_MeshSmesh.setIcon(icon)
    self.PB_MeshSmesh.setToolTip("source mesh from Salome Object Browser")
    icon = QIcon()
    icon.addFile(os.path.join(self.iconfolder,"open.png"))
    self.PB_MeshFile.setIcon(icon)
    self.PB_MeshFile.setToolTip("source mesh from a file in disk")

    self.LE_MeshFile.setText("")
    self.LE_MeshSmesh.setText("")
    self.LE_SandboxL_1.setText("")
    self.LE_SandboxR_1.setText("")

    self.SP_Hmax.setMaximum(sys.float_info.max)
    self.SP_Geomapp.setMaximum(sys.float_info.max)
    self.SP_Gradation.setMaximum(sys.float_info.max)
    self.SP_Hmin.setMinimum(10**-14)
    self.SP_Hmax.setMinimum(10**-14)
    self.SP_Hmin.setDecimals(8)
    self.SP_Hmax.setDecimals(8)
    self.updateHmaxValue()
    self.updateHminValue()

    self.sandboxes = [(self.LE_SandboxL_1, self.LE_SandboxR_1)]

    self.resize(800, 600)
    self.clean()
    self.NbOptParam = 0

    self.MyIconsFolder=os.path.join(os.environ["SMESH_ROOT_DIR"], "share", "salome", "plugins", "smesh", "mmgplugin")
    pixmap = QPixmap(os.path.join(self.MyIconsFolder,'info.png'))
    self.label_info.setPixmap(pixmap)
    self.label_info.setCursor(Qt.PointingHandCursor)

    self.maFenetre = None

  def connecterSignaux(self) :
    self.PB_Cancel.clicked.connect(self.PBCancelPressed)
    self.PB_Default.clicked.connect(self.clean)
    self.PB_Help.clicked.connect(self.PBHelpPressed)
    self.PB_OK.clicked.connect(self.PBOKPressed)

    self.LE_MeshFile.returnPressed.connect(self.meshFileNameChanged)
    self.LE_MeshSmesh.returnPressed.connect(self.meshSmeshNameChanged)
    self.PB_MeshFile.clicked.connect(self.PBMeshFilePressed)
    self.PB_MeshSmesh.clicked.connect(self.PBMeshSmeshPressed)
    self.PB_Plus.clicked.connect(self.PBPlusPressed)

    self.SP_Hmin.valueChanged.connect(self.updateHmaxValue)
    self.SP_Hmax.valueChanged.connect(self.updateHminValue)

    self.CB_RepairBeforeCompute.stateChanged.connect(self.RepairBeforeComputeStateChanged)
    self.CB_RepairOnly.stateChanged.connect(self.RepairOnlyStateChanged)
    self.CB_GenRepair.stateChanged.connect(self.GenRepairStateChanged)

    self.COB_Remesher.currentIndexChanged.connect(self.DisplayRemesherLabel)

    self.label_info.mouseReleaseEvent = self.GetLabelEvent

    self.SP_Hmin.valueChanged.connect(self.UpdateHminDecimals)
    self.SP_Hmax.valueChanged.connect(self.UpdateHmaxDecimals)

  def UpdateHminDecimals(self, value):
    self.SP_Hmin.lineEdit().setText(str(value).rstrip('0').rstrip('.') if '.' in str(value) else str(value))

  def UpdateHmaxDecimals(self, value):
    self.SP_Hmax.lineEdit().setText(str(value).rstrip('0').rstrip('.') if '.' in str(value) else str(value))

  def GenMedFromAny(self, fileIn):
    if fileIn.endswith('.med'):
      return
    from salome.smesh import smeshBuilder
    smesh = smeshBuilder.New()
    self.fichierIn=tempfile.mktemp(suffix=".med",prefix="ForMMG_")
    if os.path.exists(self.fichierIn):
      os.remove(self.fichierIn)

    ext = os.path.splitext(fileIn)[-1]
    if ext == '.mesh' or ext == '.meshb':
      TmpMesh = smesh.CreateMeshesFromGMF(fileIn)[0]
    elif ext == '.cgns':
      TmpMesh = smesh.CreateMeshesFromCGNS(fileIn)[0][0]
    elif ext == '.stl':
      TmpMesh = smesh.CreateMeshesFromSTL(fileIn)
    elif ext == '.unv':
      TmpMesh = smesh.CreateMeshesFromUNV(fileIn)
    TmpMesh.ExportMED(self.fichierIn, autoDimension=True)
    smesh.RemoveMesh(TmpMesh)
    """
    TmpMesh = meshio.read(fileIn)
    TmpMesh.write(self.fichierIn, 'med')
    """

  def GenMeshFromMed(self):
    create_mesh = False
    if self.__selectedMesh is None:
      from salome.smesh import smeshBuilder
      smesh = smeshBuilder.New()
      self.__selectedMesh = smesh.CreateMeshesFromMED(self.fichierIn)[0][0]
      create_mesh = True
    self.fichierIn=tempfile.mktemp(suffix=".mesh",prefix="ForMMG_")
    if os.path.exists(self.fichierIn):
      os.remove(self.fichierIn)

    if self.__selectedMesh is not None:
      if str(type(self.__selectedMesh)) == "<class 'salome.smesh.smeshBuilder.Mesh'>":
        self.__selectedMesh.ExportGMF(self.fichierIn)
      else:
        self.__selectedMesh.ExportGMF(self.__selectedMesh, self.fichierIn, True)
    else:
      QMessageBox.critical(self, "Mesh", "internal error")
    if create_mesh:
        smesh.RemoveMesh(self.__selectedMesh)

  def GetLabelEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.showInfo()

  def showInfo(self):
    title = "How to use the sandbox with "
    message ="""** Generic options
-h        Print this message
-v [n]    Tune level of verbosity, [-1..10]
-m [n]    Set maximal memory size to n Mbytes
-d        Turn on debug mode
-val      Print the default parameters values
-default  Save a local parameters file for default parameters values

**  File specifications
-sol file  load solution or metric file
-met file  load metric file

**  Mode specifications (mesh adaptation by default)
-ls     val create mesh of isovalue val (0 if no argument provided)
-lssurf val split mesh boundaries on isovalue val (0 if no argument
                provided)

**  Parameters
-A           enable anisotropy (without metric file).
-ar     val  angle detection
-nr          no angle detection
-hausd  val  control Hausdorff distance
-hgrad  val  control gradation
-hmax   val  maximal mesh size
-hmin   val  minimal mesh size
-hsiz   val  constant mesh size
-rmc   [val] enable the removal of components whose volume
                    fraction is less than val (1e-5 if not given)
                    of the mesh volume (level-set mode only).
"""
    if self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      title+="MMGS"
      message +="""-keep-ref    preserve initial domain references in level-set mode.
-rn [n]      Turn on or off the renumbering using SCOTCH [0/1]
"""
    elif self.COB_Remesher.currentIndex() == REMESHER_DICT['MMG2D']:
      title+="MMG2D"
      message+="""-opnbdy      preserve input triangles at the interface of two domains
                    of the same reference.
-3dMedit val read and write for gmsh visu: output only if val=1,
                    input and output if val=2, input if val=3
-nofem       do not force Mmg to create a finite element mesh
-nosurf      no surface modifications
"""
    else:
      title+="MMG3D"
      message+="""-opnbdy      preserve input triangles at the interface of two domains
                    of the same reference.
-octree val  specify the max number of points per octree cell
-rn [n]      turn on or off the renumbering using SCOTCH [1/0]
-nofem       do not force Mmg to create a finite element mesh
-nosurf      no surface modifications
"""

    message+="""
-noinsert    no point insertion/deletion
-nomove      no point relocation
-noswap      no edge or face flipping
-nreg   val  normal regularization on(val=1) or off(val=0).
-xreg        regularization of boundary point positions
-nsd    val  save the subdomain number val (0==all subdomain)
-optim       mesh optimization
"""
    if self.COB_Remesher.currentIndex() == REMESHER_DICT['MMG3D']:
      message+="""
-optimLES    enable skewness improvement (for LES computations)
"""

    message+="""
**  Parameters for advanced users
-nosizreq       disable setting of required edge sizes over required
                        vertices.
-hgradreq  val  control gradation from required entities toward
                        others"""

    QMessageBox.about(None, title, message)


  def DisplayRemesherLabel(self):
    from PyQt5 import QtCore, QtGui, QtWidgets
    _translate = QtCore.QCoreApplication.translate
    if self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      self.label_Remesher.setText(_translate("MyPlugDialog", "This remesher handles triangular surface meshes in 3D."))
    elif self.COB_Remesher.currentIndex() == REMESHER_DICT['MMG2D']:
      self.label_Remesher.setText(_translate("MyPlugDialog", "This remesher handles two-dimensional triangular meshes."))
    else:
      self.label_Remesher.setText(_translate("MyPlugDialog", "This remesher handles tetrahedral volume meshes. It performs surface and volume modifications."))

  def RepairBeforeComputeStateChanged(self, state):
    if state == 2: # Checked
      self.CB_RepairOnly.setChecked(False)
      self.CB_RepairOnly.setDisabled(True)

      self.CB_GenRepair.setDisabled(False)
    else:
      self.CB_RepairOnly.setDisabled(False)

      self.CB_GenRepair.setChecked(False)
      self.CB_GenRepair.setDisabled(True)

  def RepairOnlyStateChanged(self, state):
    if state == 2: # Checked
      self.CB_RepairBeforeCompute.setChecked(False)
      self.CB_RepairBeforeCompute.setDisabled(True)

      self.CB_GenRepair.setChecked(False)
      self.CB_GenRepair.setDisabled(True)
    else:
      self.CB_RepairBeforeCompute.setChecked(True)
      self.CB_RepairBeforeCompute.setDisabled(False)

      self.CB_GenRepair.setChecked(False)
      self.CB_GenRepair.setDisabled(False)

  def GenRepairStateChanged(self, state):
    if state == 2: # Checked
      self.CB_RepairBeforeCompute.setChecked(True)
      self.CB_RepairBeforeCompute.setDisabled(True)

      self.CB_RepairOnly.setChecked(False)
      self.CB_RepairOnly.setDisabled(True)
    else:
      self.CB_RepairBeforeCompute.setChecked(True)
      self.CB_RepairBeforeCompute.setDisabled(False)

      self.CB_RepairOnly.setChecked(False)
      self.CB_RepairOnly.setDisabled(False)

  def updateHmaxValue(self):
    self.SP_Hmax.setMinimum(self.SP_Hmin.value())

  def updateHminValue(self):
    self.SP_Hmin.setMaximum(self.SP_Hmax.value())

  def PBPlusPressed(self):
    for elt in self.sandboxes:
      if elt[0].text() == "":
        QMessageBox.warning(self, "Sandbox", "There is an empty line.")
        return
    self.NbOptParam+=1
    from PyQt5 import QtCore, QtGui, QtWidgets
    self.LE_SandboxL = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
    self.LE_SandboxL.setMinimumSize(QtCore.QSize(0, 30))
    self.LE_SandboxL.setObjectName("LE_SandboxL_" + str(self.NbOptParam + 1))
    self.gridLayout_5.addWidget(self.LE_SandboxL, self.NbOptParam + 1, 0, 1, 1)

    self.LE_SandboxR = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
    self.LE_SandboxR.setMinimumSize(QtCore.QSize(0, 30))
    self.LE_SandboxR.setObjectName("LE_SandboxR_" + str(self.NbOptParam + 1))
    self.gridLayout_5.addWidget(self.LE_SandboxR, self.NbOptParam + 1, 1, 1, 1)

    spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.gridLayout_5.addItem(spacerItem1, self.NbOptParam + 2, 0, 1, 1)
    spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.gridLayout_5.addItem(spacerItem2, self.NbOptParam + 2, 1, 1, 1)
    self.gridLayout_5.setRowStretch(self.NbOptParam + 1,0)
    self.gridLayout_5.setRowStretch(self.NbOptParam + 2,0)

    self.sandboxes.append((self.LE_SandboxL, self.LE_SandboxR))

  def PBHelpPressed(self):
    QMessageBox.about(self, "About this MMG remeshing tool",
            """
                    Adapt your mesh with MMG
                    -------------------------------------------

This tool allows your to adapt your mesh after a
Boolean operation. It also allows you to repair a
bad mesh (double elements or free elements).

By default, your mesh will be prepared for MMG.
You can find the options to disable it or
explicitly generate the repaired mesh in the
'Advanced Remeshing Options' panel.
By pressing the 'Remesh' button, your mesh will
be adapted by MMG with your selected parameters.
You can change the parameters to better fit you
needs than with the default ones. Restore the
default parameters by clicking on the 'Compute
Default Values' button.
            """)

  def Repair(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False
    if self.values is None:
      QMessageBox.critical(self, "Mesh", "internal error, check the logs")
      return False
    if self.fichierIn != "":
        self.values.MeshName = self.fichierIn
    if self.MeshIn != "":
        self.values.MeshName = self.MeshIn
    if self.values.CpyName.endswith('_0'):
      self.values.DeleteMesh()

    self.values.CpyName = re.sub(r'\d*$', '', self.values.CpyName) + str(self.numRepair)

    if self.isFile:
      self.values.CpyMesh = self.values.smesh_builder.CreateMeshesFromMED(self.values.MeshName)[0][0]
      self.values.CpyMesh.SetName(self.values.CpyName)
    else:
      if self.values.SelectedObject is None:
        self.values.SelectedObject = self.values.study.FindObjectByName(self.values.MeshName, 'SMESH')[-1]
      self.values.CpyMesh = self.values.smesh_builder.CopyMesh(self.values.SelectedObject.GetObject(), self.values.CpyName, True, True)

    self.numRepair+=1
    self.values.AnalysisAndRepair(self.CB_GenRepair.isChecked() or self.CB_RepairOnly.isChecked())

  def PBOKPressed(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False

    ext = os.path.splitext(self.fichierIn)[-1]
    if self.isFile and ext != '.med' \
        and self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      if not ((ext == 'mesh' or ext == '.meshb') and not (self.CB_RepairBeforeCompute.isChecked() or self.CB_RepairOnly.isChecked())):
          self.GenMedFromAny(self.fichierIn)

    CpyFichierIn = self.fichierIn
    CpyMeshIn = self.MeshIn
    CpySelectedMesh = self.__selectedMesh
    if (self.CB_RepairBeforeCompute.isChecked() or self.CB_RepairOnly.isChecked()) and self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      if self.values is None:
        if self.fichierIn != "":
          self.values = Values(self.fichierIn, 0, self.currentName)
        else:
          self.values = Values(self.MeshIn, 0, self.currentName)
      self.Repair()
      if not self.CB_GenRepair.isChecked() and not self.CB_RepairOnly.isChecked():
        self.numRepair-=1
    if not self.CB_RepairOnly.isChecked():
      ext = os.path.splitext(self.fichierIn)[-1]
      if self.fichierIn != "":
        if ext == '.med':
          self.GenMeshFromMed()
        elif ext != '.mesh' and ext != '.meshb':
          self.GenMedFromAny(self.fichierIn)
          self.GenMeshFromMed()
        self.__selectedMesh = None

      if not(self.PrepareLigneCommande()):
        #warning done yet
        #QMessageBox.warning(self, "Compute", "Command not found")
        return False

      self.maFenetre=MyViewText(self,self.commande)
      if (not self.CB_GenRepair.isChecked()) and self.values is not None:
        self.values.DeleteMesh()

    self.fichierIn = CpyFichierIn
    self.MeshIn = CpyMeshIn
    self.__selectedMesh = CpySelectedMesh
    self.values = None
    return True

  def enregistreResultat(self):
    import salome
    import SMESH
    from salome.kernel import studyedit
    from salome.smesh import smeshBuilder
    smesh = smeshBuilder.New()

    if not os.path.isfile(self.fichierOut):
      QMessageBox.warning(self, "Compute", "Result file "+self.fichierOut+" not found")

    maStudy=salome.myStudy
    smesh.UpdateStudy()
    self.GenMedFromAny(self.fichierOut)
    (outputMesh, status) = smesh.CreateMeshesFromMED(self.fichierIn)
    outputMesh=outputMesh[0]
    name=str(self.LE_MeshSmesh.text())
    initialMeshFile=None
    initialMeshObject=None
    if name=="":
      if self.MeshIn =="":
        a = re.sub(r'_\d*$', '', str(self.fichierIn))
      else: # Repaired
        a = re.sub(r'_\d*$', '', str(self.MeshIn))
      name=os.path.basename(os.path.splitext(a)[0])
      initialMeshFile=a

    else:
      initialMeshObject=maStudy.FindObjectByName(name ,"SMESH")[0]

    meshname = self.currentName+"_MMG_"+str(self.num)
    smesh.SetName(outputMesh.GetMesh(), meshname)
    outputMesh.Compute() #no algorithms message for "Mesh_x" has been computed with warnings: -  global 1D algorithm is missing

    self.editor = studyedit.getStudyEditor()
    moduleEntry=self.editor.findOrCreateComponent("SMESH","SMESH")
    HypReMeshEntry = self.editor.findOrCreateItem(
        moduleEntry, name = "Plugins Hypotheses", icon="mesh_tree_hypo.png") #, comment = "HypoForRemeshing" )

    monStudyBuilder=maStudy.NewBuilder()
    monStudyBuilder.NewCommand()
    newStudyIter=monStudyBuilder.NewObject(HypReMeshEntry)
    self.editor.setAttributeValue(newStudyIter, "AttributeName", "MMG Parameters_"+str(self.num))
    self.editor.setAttributeValue(newStudyIter, "AttributeComment", self.getResumeData(separator=" ; "))

    SOMesh=maStudy.FindObjectByName(meshname ,"SMESH")[0]

    if initialMeshFile!=None:
      newStudyFileName=monStudyBuilder.NewObject(SOMesh)
      self.editor.setAttributeValue(newStudyFileName, "AttributeName", "meshFile")
      self.editor.setAttributeValue(newStudyFileName, "AttributeExternalFileDef", initialMeshFile)
      self.editor.setAttributeValue(newStudyFileName, "AttributeComment", initialMeshFile)

    if initialMeshObject!=None:
      newLink=monStudyBuilder.NewObject(SOMesh)
      monStudyBuilder.Addreference(newLink, initialMeshObject)

    newLink=monStudyBuilder.NewObject(SOMesh)
    monStudyBuilder.Addreference(newLink, newStudyIter)

    if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()
    self.num+=1
    return True

  def getResumeData(self, separator="\n"):
    text=""
    text+="RepairBeforeCompute="+str(self.CB_RepairBeforeCompute.isChecked())+separator
    text+="SwapEdge="+str(self.CB_SwapEdge.isChecked())+separator
    text+="MoveEdge="+str(self.CB_MoveEdge.isChecked())+separator
    text+="InsertEdge="+str(self.CB_InsertEdge.isChecked())+separator
    text+="GeometricalApproximation="+str(self.SP_Geomapp.value())+separator
    text+="Hmin="+str(self.SP_Hmin.value())+separator
    text+="Hmax="+str(self.SP_Hmax.value())+separator
    text+="MeshGradation="+str(self.SP_Gradation.value())+separator
    return str(text)

  def PBCancelPressed(self):
    self.close()

  def PBMeshFilePressed(self):
    filter_string = "All mesh formats (*.unv *.cgns *.mesh *.meshb *.med *.stl)"

    fd = QFileDialog(self, "select an existing mesh file", self.LE_MeshFile.text(), filter_string + ";;All Files (*)")
    if fd.exec_():
      infile = fd.selectedFiles()[0]
      self.LE_MeshFile.setText(infile)
      self.fichierIn=str(infile)
      self.currentName = os.path.splitext(os.path.basename(self.fichierIn))[0]
      """
      if self.values is not None:
        self.values.DeleteMesh()
      self.values = None
      self.values = Values(self.fichierIn, 0, self.currentName)
      """
      self.MeshIn=""
      self.LE_MeshSmesh.setText("")
      self.__selectedMesh=None
      self.isFile = True

  def PBMeshSmeshPressed(self):
    from omniORB import CORBA
    import salome
    from salome.kernel import studyedit
    from salome.smesh.smeshstudytools import SMeshStudyTools
    from salome.gui import helper as guihelper
    from salome.smesh import smeshBuilder
    smesh = smeshBuilder.New()

    mySObject, myEntry = guihelper.getSObjectSelected()
    if CORBA.is_nil(mySObject) or mySObject==None:
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return
    self.smeshStudyTool = SMeshStudyTools()
    try:
      self.__selectedMesh = self.smeshStudyTool.getMeshObjectFromSObject(mySObject)
    except:
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return
    if CORBA.is_nil(self.__selectedMesh):
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return
    myName = mySObject.GetName()

    self.MeshIn=myName
    self.currentName = myName
    """
    if self.values is not None:
        self.values.DeleteMesh()
    self.values = None
    self.values = Values(myName, 0, self.currentName)
    """
    self.LE_MeshSmesh.setText(myName)
    self.LE_MeshFile.setText("")
    self.fichierIn=""
    self.isFile = False

  def meshFileNameChanged(self):
    #FIXME Change in name Gen new med
    self.fichierIn=str(self.LE_MeshFile.text())
    if os.path.exists(self.fichierIn):
      self.__selectedMesh=None
      self.MeshIn=""
      self.LE_MeshSmesh.setText("")
      self.currentname = os.path.basename(self.fichierIn)
      return
    QMessageBox.warning(self, "Mesh file", "File doesn't exist")

  def meshSmeshNameChanged(self):
    """only change by GUI mouse selection, otherwise clear"""
    self.__selectedMesh = None
    self.MeshIn=""
    self.LE_MeshSmesh.setText("")
    self.fichierIn=""
    return

  def prepareFichier(self):
    self.GenMeshFromMed()

  def PrepareLigneCommande(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False
    if self.__selectedMesh is not None: self.prepareFichier()
    if not (os.path.isfile(self.fichierIn)):
      QMessageBox.critical(self, "File", "unable to read GMF Mesh in "+str(self.fichierIn))
      return False

    self.commande=""
    selected_index = self.COB_Remesher.currentIndex()
    if selected_index == REMESHER_DICT['MMGS']:
        self.commande = "mmgs_O3" if platform.system() != "Windows" else  "mmgs.exe"
    elif selected_index == REMESHER_DICT['MMG2D']:
      self.commande = "mmg2d_O3" if platform.system() != "Windows" else  "mmg2d.exe"
    elif selected_index == REMESHER_DICT['MMG3D']:
      self.commande = "mmg3d_O3" if platform.system() != "Windows" else  "mmg3d.exe"
    else:
      self.commande = "mmgs_O3" if platform.system() != "Windows" else  "mmgs.exe"

    deb=os.path.splitext(self.fichierIn)
    self.fichierOut=deb[0] + "_output.mesh"

    for elt in self.sandboxes:
      self.commande+=' ' + elt[0].text() + ' ' + elt[1].text()

    if not self.CB_InsertEdge.isChecked() : self.commande+=" -noinsert"
    if not self.CB_SwapEdge.isChecked()  : self.commande+=" -noswap"
    if not self.CB_MoveEdge.isChecked()  : self.commande+=" -nomove"
    if self.SP_Geomapp.value() != 0.01 : self.commande+=" -hausd %f"%self.SP_Geomapp.value()
    self.commande+=" -hmin %f"   %self.SP_Hmin.value()
    self.commande+=" -hmax %f"   %self.SP_Hmax.value()
    if self.SP_Gradation.value() != 1.3   : self.commande+=" -hgrad %f"  %self.SP_Gradation.value()

    self.commande+=' -in "'  + self.fichierIn +'"'
    self.commande+=' -out "' + self.fichierOut +'"'

    if verbose: print("INFO: MMG command:\n  %s\n*WARNING* Copy-paste the command line in your study if you want to dump it." % self.commande)
    return True

  def clean(self):
    if self.values is None and self.currentName != "" and self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      if self.fichierIn != "":
        cpy = self.fichierIn
        self.GenMedFromAny(self.fichierIn)
        self.values = Values(self.fichierIn, 0, self.currentName)
        self.fichierIn = cpy
      elif self.MeshIn != "":
        self.values = Values(self.MeshIn, 0, self.currentName)

    if self.values is not None:
      self.values.ComputeNewDefaultValues()
      self.SP_Geomapp.setProperty("value", self.values.geomapp)
      self.SP_Gradation.setProperty("value", self.values.hgrad)
      self.SP_Hmin.setProperty("value", self.values.hmin)
      self.SP_Hmax.setProperty("value", self.values.hmax)
      self.values.DeleteMesh()

    else: # No file provided, default from MMG
      self.SP_Geomapp.setProperty("value", 0.01)
      self.SP_Gradation.setProperty("value", 1.3)
      self.SP_Hmin.setProperty("value", 0.01)
      self.SP_Hmax.setProperty("value", 10)
    self.values = None
    self.CB_InsertEdge.setChecked(True)
    self.CB_MoveEdge.setChecked(True)
    self.CB_SwapEdge.setChecked(True)
    self.CB_RepairBeforeCompute.setChecked(True)
    self.CB_RepairOnly.setChecked(False)
    self.CB_GenRepair.setChecked(False)
    #self.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMGS'])

    from PyQt5 import QtCore, QtGui, QtWidgets
    _translate = QtCore.QCoreApplication.translate
    for i in reversed(range(self.gridLayout_5.count())):
      widget = self.gridLayout_5.takeAt(i).widget()
      if widget is not None:
        widget.setParent(None)

    self.LE_SandboxR_1 = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
    self.LE_SandboxR_1.setMinimumSize(QtCore.QSize(0, 30))
    self.LE_SandboxR_1.setObjectName("LE_SandboxR_1")
    self.gridLayout_5.addWidget(self.LE_SandboxR_1, 1, 1, 1, 1)

    self.LE_SandboxL_1 = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
    self.LE_SandboxL_1.setMinimumSize(QtCore.QSize(0, 30))
    self.LE_SandboxL_1.setObjectName("LE_SandboxL_1")
    self.gridLayout_5.addWidget(self.LE_SandboxL_1, 1, 0, 1, 1)

    self.label_3 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
    self.label_3.setObjectName("label_3")
    self.gridLayout_5.addWidget(self.label_3, 0, 1, 1, 1)

    self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
    self.label_2.setObjectName("label_2")
    self.gridLayout_5.addWidget(self.label_2, 0, 0, 1, 1)

    spacerItem16 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    self.gridLayout_5.addItem(spacerItem16, 2, 0, 1, 1)

    spacerItem17 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    self.gridLayout_5.addItem(spacerItem17, 2, 1, 1, 1)

    self.gridLayout_5.setRowStretch(0,0)
    self.gridLayout_5.setRowStretch(1,0)
    self.gridLayout_5.setRowStretch(2,0)

    self.label_3.setText(_translate("MyPlugDialog", "Value"))
    self.label_2.setText(_translate("MyPlugDialog", "Parameter"))

    self.LE_SandboxL_1.setText("")
    self.LE_SandboxR_1.setText("")
    self.sandboxes = [(self.LE_SandboxL_1, self.LE_SandboxR_1)]

    #self.PBMeshSmeshPressed() #do not that! problem if done in load surfopt hypo from object browser
    self.TWOptions.setCurrentIndex(0) # Reset current active tab to the first tab
    value = self.SP_Hmin.value()
    self.UpdateHminDecimals(value)
    value = self.SP_Hmax.value()
    self.UpdateHmaxDecimals(value)

__dialog=None
def getDialog():
  """
  This function returns a singleton instance of the plugin dialog.
  It is mandatory in order to call show without a parent ...
  """
  global __dialog
  if __dialog is None:
    __dialog = MyMmgPlugDialog()
  #else :
  #  __dialog.clean()
  return __dialog

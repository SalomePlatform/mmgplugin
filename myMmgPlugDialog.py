# -*- coding: utf-8 -*-
# Copyright (C) 2007-2023  EDF
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

    # complex with QResources: not used
    # The icon are supposed to be located in the $SMESH_ROOT_DIR/share/salome/resources/smesh folder,
    # other solution could be in the same folder than this python module file:
    # iconfolder=os.path.dirname(os.path.abspath(__file__))

    self.iconfolder=os.path.join(os.environ["SMESH_ROOT_DIR"], "share", "salome", "resources", "smesh")
    #print "MGSurfOptPlugDialog iconfolder",iconfolder
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
    self.SP_Ridge.setMaximum(180)
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

  def connecterSignaux(self) :
    self.PB_Cancel.clicked.connect(self.PBCancelPressed)
    self.PB_Default.clicked.connect(self.clean)
    self.PB_Help.clicked.connect(self.PBHelpPressed)
    self.PB_OK.clicked.connect(self.PBOKPressed)
    
    self.LE_MeshFile.returnPressed.connect(self.meshFileNameChanged)
    self.LE_MeshSmesh.returnPressed.connect(self.meshSmeshNameChanged)
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

  def GetLabelEvent(self, event):
      from PyQt5.QtCore import Qt
      if event.button() == Qt.LeftButton:
          self.showInfo()

  def showInfo(self):
    if self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
        QMessageBox.about(None, "How to use the sandbox with MMGS",
                """
** Generic options
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
-lssurf val split mesh boundaries on isovalue val (0 if no argument provided)

**  Parameters
-A           enable anisotropy (without metric file).
-ar     val  angle detection
-nr          no angle detection
-hausd  val  control Hausdorff distance
-hgrad  val  control gradation
-hmax   val  maximal mesh size
-hmin   val  minimal mesh size
-hsiz   val  constant mesh size
-rmc   [val] enable the removal of componants whose volume fraction is less than
             val (1e-5 if not given) of the mesh volume (ls mode).
-keep-ref    preserve initial domain references in level-set mode.
-rn [n]      Turn on or off the renumbering using SCOTCH [0/1]

-noinsert    no point insertion/deletion
-nomove      no point relocation
-noswap      no edge or face flipping
-nreg        normal regul.
-xreg        vertex regul.
-nsd    val  save the subdomain number val (0==all subdomain)
-optim       mesh optimization

**  Parameters for advanced users
-nosizreq       disable setting of required edge sizes over required vertices.
-hgradreq  val  control gradation from required entities toward others
                """)
    elif self.COB_Remesher.currentIndex() == REMESHER_DICT['MMG2D']:
        QMessageBox.about(None, "How to use the sandbox with MMG2D",
                """
** Generic options
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
-lssurf val split mesh boundaries on isovalue val (0 if no argument provided)

**  Parameters
-A           enable anisotropy (without metric file).
-ar     val  angle detection
-nr          no angle detection
-hausd  val  control Hausdorff distance
-hgrad  val  control gradation
-hmax   val  maximal mesh size
-hmin   val  minimal mesh size
-hsiz   val  constant mesh size
-rmc   [val] enable the removal of componants whose volume fraction is less than
             val (1e-5 if not given) of the mesh volume (ls mode).
-opnbdy      preserve input triangles at the interface of two domains of the same reference.
-3dMedit val read and write for gmsh visu: output only if val=1, input and output if val=2, input if val=3

-nofem       do not force Mmg to create a finite element mesh 
-nosurf      no surface modifications
-noinsert    no point insertion/deletion 
-nomove      no point relocation
-noswap      no edge or face flipping
-nreg        normal regul.
-xreg        vertex regul.
-nsd    val  save the subdomain number val (0==all subdomain)
-optim       mesh optimization

**  Parameters for advanced users
-nosizreq       disable setting of required edge sizes over required vertices.
-hgradreq  val  control gradation from required entities toward others
                """)
    else:
        QMessageBox.about(None, "How to use the sandbox with MMG3D",
                """
** Generic options
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
-lssurf val split mesh boundaries on isovalue val (0 if no argument provided)

**  Parameters
-A           enable anisotropy (without metric file).
-ar     val  angle detection
-nr          no angle detection
-hausd  val  control Hausdorff distance
-hgrad  val  control gradation
-hmax   val  maximal mesh size
-hmin   val  minimal mesh size
-hsiz   val  constant mesh size
-rmc   [val] enable the removal of componants whose volume fraction is less than
             val (1e-5 if not given) of the mesh volume (ls mode).
-opnbdy      preserve input triangles at the interface of two domains of the same reference.
-octree val  specify the max number of points per octree cell 
-rn [n]      turn on or off the renumbering using SCOTCH [1/0] 

-nofem       do not force Mmg to create a finite element mesh 
-nosurf      no surface modifications

-noinsert    no point insertion/deletion 
-nomove      no point relocation
-noswap      no edge or face flipping
-nreg        normal regul.
-xreg        vertex regul.
-nsd    val  save the subdomain number val (0==all subdomain)
-optim       mesh optimization
-optimLES    enable skewness improvement (for LES computations)

**  Parameters for advanced users
-nosizreq       disable setting of required edge sizes over required vertices.
-hgradreq  val  control gradation from required entities toward others
                """)


  def DisplayRemesherLabel(self):
    from PyQt5 import QtCore, QtGui, QtWidgets
    _translate = QtCore.QCoreApplication.translate
    if self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      self.label_Remesher.setText(_translate("MyPlugDialog", "This remesher handles triangular surface meshes in 3D."))
    elif self.COB_Remesher.currentIndex() == REMESHER_DICT['MMG2D']:
      self.label_Remesher.setText(_translate("MyPlugDialog", "This remesher handles two-dimensionnal triangular meshes."))
    else:
      self.label_Remesher.setText(_translate("MyPlugDialog", "This remesher handles tetrahedral volume meshes. It performs surface and volume modifications."))

  def RepairBeforeComputeStateChanged(self, state):
      if state == 2: # Checked
          self.CB_RepairOnly.setChecked(False)
          self.CB_RepairOnly.setDisabled(True)

          self.CB_GenRepair.setDisabled(False)
          #self.CB_GenRepair.setChecked(False)
      else:
          #self.CB_RepairOnly.setChecked(False)
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
    QMessageBox.about(None, "About this MMG remeshing tool",
            """
                    Adapt your mesh with MMG
                    -------------------------------------------

This tool allows your to adapt your mesh after a
Boolean operation. It also allows you to repair a
bad mesh (double elements or free elements).

By pressing the 'Repair' button, you will generate a
new mesh prepared for MMG from your input mesh.
By pressing the 'Compute' button, you will repair
your imput mesh if needed and adapt it with MMG with
your selected parameters.
You can change the parameters to better fit you
needs than with the default ones. Restore the
default parameters by clicking on the 'Default'
button.
            """)

  def Repair(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False
    if self.values is None:
      QMessageBox.critical(self, "Mesh", "internal error, check the logs")
      return False
    if self.values.CpyName.endswith('_0'):
      self.values.DeleteMesh()

    self.values.CpyName = re.sub(r'\d*$', '', self.values.CpyName) + str(self.numRepair)

    if self.isFile:
      self.values.CpyMesh = self.values.smesh_builder.CreateMeshesFromGMF(self.values.MeshName)[0]
      self.values.CpyMesh.SetName(self.values.CpyName)
    else:
      self.values.CpyMesh = self.values.smesh_builder.CopyMesh(self.values.SelectedObject.GetObject(), self.values.CpyName, True, True)
      
    self.numRepair+=1
    self.values.AnalysisAndRepair(self.CB_GenRepair.isChecked() or self.CB_RepairOnly.isChecked())

  def PBOKPressed(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False
    if not self.CB_RepairBeforeCompute.isChecked() and not self.CB_RepairOnly.isChecked():
      QMessageBox.warning(self, "Compute", "No actions triggered. Please set one in Advanced Remeshing Options.")
      return False

    CpyFichierIn = self.fichierIn
    CpyMeshIn = self.MeshIn
    CpySelectedMesh = self.__selectedMesh
    if (self.CB_RepairBeforeCompute.isChecked() or self.CB_RepairOnly.isChecked()) and self.COB_Remesher.currentIndex() == REMESHER_DICT['MMGS']:
      if self.values is None:
        if self.fichierIn != "":
          self.values = Values(self.fichierIn, 0)
        else:
          self.values = Values(self.MeshIn, 0)
      self.Repair()
      if not self.CB_GenRepair.isChecked() and not self.CB_RepairOnly.isChecked():
          self.numRepair-=1
      self.MeshIn = self.values.CpyName
      self.fichierIn=""
      self.__selectedMesh = self.values.CpyMesh
    if not self.CB_RepairOnly.isChecked():
      if not(self.PrepareLigneCommande()):
        #warning done yet
        #QMessageBox.warning(self, "Compute", "Command not found")
        return
        
      maFenetre=MyViewText(self,self.commande)
      if not self.CB_GenRepair.isChecked():
          self.values.DeleteMesh()

    self.fichierIn = CpyFichierIn
    self.MeshIn = CpyMeshIn
    self.__selectedMesh = CpySelectedMesh
    self.values.CpyMesh = None

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
    (outputMesh, status) = smesh.CreateMeshesFromGMF(self.fichierOut)
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

    meshname = name+"_MMG_"+str(self.num)
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

  def PBSavePressed(self):
    from datetime import datetime
    if not(self.PrepareLigneCommande()): return
    text = "# MMG hypothesis parameters\n"
    text += "# Params for mesh : " +  self.LE_MeshSmesh.text() +"\n"
    text += datetime.now().strftime("# Date : %d/%m/%y %H:%M:%S\n")
    text += "# Command : "+self.commande+"\n"
    text += self.getResumeData(separator="\n")
    text += "\n\n"

    try:
      f=open(self.paramsFile,"a")
    except:
      QMessageBox.warning(self, "File", "Unable to open "+self.paramsFile)
      return
    try:
      f.write(text)
    except:
      QMessageBox.warning(self, "File", "Unable to write "+self.paramsFile)
      return
    f.close()

  def SP_toStr(self, widget):
    """only for a QLineEdit widget"""
    #cr, pos=widget.validator().validate(res, 0) #n.b. "1,3" is acceptable !locale!
    try:
      val=float(widget.text())
    except:
      QMessageBox.warning(self, widget.titleForWarning, "float value is incorrect: '"+widget.text()+"'")
      res=str(widget.validator().bottom())
      widget.setProperty("text", res)
      return res
    valtest=widget.validator().bottom()
    if valtest!=None:
      if val<valtest:
        QMessageBox.warning(self, widget.titleForWarning, "float value is under minimum: "+str(val)+" < "+str(valtest))
        res=str(valtest)
        widget.setProperty("text", res)
        return res
    valtest=widget.validator().top()
    if valtest!=None:
      if val>valtest:
        QMessageBox.warning(self, widget.titleForWarning, "float value is over maximum: "+str(val)+" > "+str(valtest))
        res=str(valtest)
        widget.setProperty("text", res)
        return res    
    return str(val)

  def getResumeData(self, separator="\n"):
    text=""
    text+="RepairBeforeCompute="+str(self.CB_RepairBeforeCompute.isChecked())+separator
    text+="SwapEdge="+str(self.CB_SwapEdge.isChecked())+separator
    text+="MoveEdge="+str(self.CB_MoveEdge.isChecked())+separator
    text+="InsertEdge="+str(self.CB_InsertEdge.isChecked())+separator
    text+="GeometricalApproximation="+str(self.SP_Geomapp.value())+separator
    text+="RidgeAngle="+str(self.SP_Ridge.value())+separator
    text+="Hmin="+str(self.SP_Hmin.value())+separator
    text+="Hmax="+str(self.SP_Hmax.value())+separator
    text+="MeshGradation="+str(self.SP_Gradation.value())+separator
    return str(text)

  def PBCancelPressed(self):
    self.close()

  def PBMeshFilePressed(self):
    fd = QFileDialog(self, "select an existing Mesh file", self.LE_MeshFile.text(), "Mesh-Files (*.mesh);;All Files (*)")
    if fd.exec_():
      infile = fd.selectedFiles()[0]
      self.LE_MeshFile.setText(infile)
      self.fichierIn=str(infile)
      if self.values is not None:
        self.values.DeleteMesh()
      self.values = None
      self.values = Values(self.fichierIn, 0)
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
      #self.LE_MeshSmesh.setText("")
      #self.MeshIn=""
      #self.LE_MeshFile.setText("")
      #self.fichierIn=""
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

    if self.values is not None:
        self.values.DeleteMesh()
    self.values = None
    self.values = Values(myName, 0)
    #print "MeshSmeshNameChanged", myName
    self.MeshIn=myName
    self.LE_MeshSmesh.setText(myName)
    self.LE_MeshFile.setText("")
    self.fichierIn=""
    self.isFile = False

  def meshFileNameChanged(self):
    self.fichierIn=str(self.LE_MeshFile.text())
    #print "meshFileNameChanged", self.fichierIn
    if os.path.exists(self.fichierIn): 
      self.__selectedMesh=None
      self.MeshIn=""
      self.LE_MeshSmesh.setText("")
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
    self.fichierIn=tempfile.mktemp(suffix=".mesh",prefix="ForMMG_")
    if os.path.exists(self.fichierIn):
        os.remove(self.fichierIn)
    if str(type(self.__selectedMesh)) == "<class 'salome.smesh.smeshBuilder.Mesh'>":
        self.__selectedMesh.ExportGMF(self.fichierIn)
    else:
        self.__selectedMesh.ExportGMF(self.__selectedMesh, self.fichierIn, True)

  def PrepareLigneCommande(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False
    if self.__selectedMesh!=None: self.prepareFichier()
    if not (os.path.isfile(self.fichierIn)):
      QMessageBox.critical(self, "File", "unable to read GMF Mesh in "+str(self.fichierIn))
      return False
    
    self.commande=""
    selected_index = self.COB_Remesher.currentIndex()
    if selected_index == REMESHER_DICT['MMGS']:
        self.commande = "mmgs_O3"
    elif selected_index == REMESHER_DICT['MMG2D']:
        self.commande = "mmg2d_O3"
    elif selected_index == REMESHER_DICT['MMG3D']:
        self.commande = "mmg3d_O3"
    else:
        self.commande = "mmgs_O3"

    deb=os.path.splitext(self.fichierIn)
    self.fichierOut=deb[0] + "_output.mesh"
    
    for elt in self.sandboxes:
        self.commande+=' ' + elt[0].text() + ' ' + elt[1].text()
    
    if not self.CB_InsertEdge.isChecked() : self.commande+=" -noinsert"
    if not self.CB_SwapEdge.isChecked()  : self.commande+=" -noswap"
    if not self.CB_MoveEdge.isChecked()  : self.commande+=" -nomove"
    if self.SP_Geomapp.value() != 0.01 : self.commande+=" -hausd %f"%self.SP_Geomapp.value()
    if self.SP_Ridge.value() != 45.0  : self.commande+=" -ar %f"%self.SP_Ridge.value()
    self.commande+=" -hmin %f"   %self.SP_Hmin.value()
    self.commande+=" -hmax %f"   %self.SP_Hmax.value()
    if self.SP_Gradation.value() != 1.3   : self.commande+=" -hgrad %f"  %self.SP_Gradation.value()

    self.commande+=' -in "'  + self.fichierIn +'"'
    self.commande+=' -out "' + self.fichierOut +'"'

    if verbose: print("INFO: MMG command:\n  %s\n*WARNING* Copy-paste the command line in your study if you want to dump it." % self.commande)
    return True

  def clean(self):
    if self.values is not None:
        self.values.ComputeNewDefaultValues()
        self.SP_Geomapp.setProperty("value", self.values.geomapp)
        self.SP_Ridge.setProperty("value", self.values.ridge)
        self.SP_Gradation.setProperty("value", self.values.hgrad)
        self.SP_Hmin.setProperty("value", self.values.hmin)
        self.SP_Hmax.setProperty("value", self.values.hmax)
    else: # No file provided, default from MMG
        self.SP_Geomapp.setProperty("value", 0.01)
        self.SP_Ridge.setProperty("value", 45.0)
        self.SP_Gradation.setProperty("value", 1.3)
        self.SP_Hmin.setProperty("value", 0.01)
        self.SP_Hmax.setProperty("value", 10)
    self.CB_InsertEdge.setChecked(True)
    self.CB_MoveEdge.setChecked(True)
    self.CB_SwapEdge.setChecked(True)
    self.CB_RepairBeforeCompute.setChecked(True)
    self.CB_RepairOnly.setChecked(False)
    self.CB_GenRepair.setChecked(False)
    self.COB_Remesher.setCurrentIndex(REMESHER_DICT['MMGS'])

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

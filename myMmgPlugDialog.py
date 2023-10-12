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
from mmgplugin.MyPlugDialog_ui import Ui_MyPlugDialog
from mmgplugin.myViewText import MyViewText
from qtsalome import *
from mmgplugin.compute_values import *

verbose = True


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
    self.__selectedMesh=None
    self.values = None

    # complex with QResources: not used
    # The icon are supposed to be located in the $SMESH_ROOT_DIR/share/salome/resources/smesh folder,
    # other solution could be in the same folder than this python module file:
    # iconfolder=os.path.dirname(os.path.abspath(__file__))

    self.iconfolder=os.environ["SMESH_ROOT_DIR"]+"/share/salome/resources/smesh"
    #print "MGSurfOptPlugDialog iconfolder",iconfolder
    icon = QIcon()
    icon.addFile(os.path.join(self.iconfolder,"select1.png"))
    self.PB_LoadHyp.setIcon(icon)
    self.PB_LoadHyp.setToolTip("hypothesis from Salome Object Browser")
    self.PB_SaveHyp.setIcon(icon)
    self.PB_SaveHyp.setToolTip("hypothesis to Salome Object Browser")
    self.PB_MeshSmesh.setIcon(icon)
    self.PB_MeshSmesh.setToolTip("source mesh from Salome Object Browser")
    icon = QIcon()
    icon.addFile(os.path.join(self.iconfolder,"open.png"))
    self.PB_MeshFile.setIcon(icon)
    self.PB_MeshFile.setToolTip("source mesh from a file in disk")

    self.LE_MeshFile.setText("")
    self.LE_MeshSmesh.setText("")

    self.resize(800, 600)
    self.clean()

  def connecterSignaux(self) :
    self.PB_Cancel.clicked.connect(self.PBCancelPressed)
    self.PB_Default.clicked.connect(self.clean)
    self.PB_Help.clicked.connect(self.PBHelpPressed)
    self.PB_Repair.clicked.connect(self.PBRepairPressed)
    self.PB_OK.clicked.connect(self.PBOKPressed)
    
    self.PB_LoadHyp.clicked.connect(self.PBLoadHypPressed)
    self.PB_SaveHyp.clicked.connect(self.PBSaveHypPressed)
    
    self.PB_MeshFile.clicked.connect(self.PBMeshFilePressed)
    self.PB_MeshSmesh.clicked.connect(self.PBMeshSmeshPressed)

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

  def PBRepairPressed(self):
    if self.fichierIn=="" and self.MeshIn=="":
      QMessageBox.critical(self, "Mesh", "select an input mesh")
      return False
    if self.values is None:
      QMessageBox.critical(self, "Mesh", "internal error, check the logs")
      return False
    self.values.CpyName = re.sub(r'\d*$', '', self.values.CpyName) + str(self.num)
    if self.values.CpyMesh is not None:
        self.values.CpyMesh.SetName(self.values.CpyName)
    self.num+=1
    self.values.AnalysisAndRepair()

  def PBOKPressed(self):
    CpyFichierIn = self.fichierIn
    CpyMeshIn = self.MeshIn
    CpySelectedMesh = self.__selectedMesh
    if self.CB_RepairBeforeCompute.isChecked() == True:
        self.PBRepairPressed()
        self.MeshIn = self.values.CpyName
        self.fichierIn=""
        self.__selectedMesh = self.values.CpyMesh
    if not(self.PrepareLigneCommande()):
      #warning done yet
      #QMessageBox.warning(self, "Compute", "Command not found")
      return
    
    maFenetre=MyViewText(self,self.commande)
    self.fichierIn = CpyFichierIn
    self.MeshIn = CpyMeshIn
    self.__selectedMesh = CpySelectedMesh

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

  def PBSaveHypPressed_risky(self):
    """
    save hypothesis in Object Browser outside GEOM ou MESH
    WARNING: at root of Object Browser is not politically correct
    """
    import salome
    
    if verbose: print("save hypothesis in Object Browser")
    
    name = "MMG"
    #how ??? icon = "mesh_tree_hypo.png"
    namei = "MMG Parameters_%i" % self.num
    datai = self.getResumeData(separator=" ; ")
    
    myStudy = salome.myStudy
    myBuilder = myStudy.NewBuilder()
    #myStudy.IsStudyLocked()
    myComponent = myStudy.FindComponent(name)
    if myComponent == None:
      print("myComponent not found, create")
      myComponent = myBuilder.NewComponent(name)
    AName = myBuilder.FindOrCreateAttribute(myComponent, "AttributeName")
    AName.SetValue(name)
    ACmt = myBuilder.FindOrCreateAttribute(myComponent, "AttributeComment")
    ACmt.SetValue(name)
    
    myObject = myBuilder.NewObject(myComponent)
    AName = myBuilder.FindOrCreateAttribute(myObject, "AttributeName")
    AName.SetValue(namei)
    ACmt = myBuilder.FindOrCreateAttribute(myObject, "AttributeComment")
    ACmt.SetValue(datai)

    if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()
    self.num += 1
    if verbose: print(("save %s in Object Browser done: %s\n%s" % (name, myObject.GetID(), datai)))
    return True

  def PBSaveHypPressed(self):
    """
    save hypothesis in Object Browser
    bug: affichage ne marche pas si inclusion dans dans GEOM ou MESH depuis salome 730
    """
    import salome
    import SMESH
    from salome.kernel import studyedit
    from salome.smesh import smeshBuilder
    #[PAL issue tracker:issue1871] Les nouveaux objets ne s'affichent pas dans SMESH
    QMessageBox.warning(self, "Save", "waiting for fix: Object Browser will not display hypothesis")
    
    if verbose: print("save hypothesis in Object Browser")
    smesh = smeshBuilder.New()

    maStudy=salome.myStudy
    smesh.UpdateStudy()

    self.editor = studyedit.getStudyEditor()
    moduleEntry=self.editor.findOrCreateComponent("SMESH","SMESH")
    HypReMeshEntry = self.editor.findOrCreateItem(
        moduleEntry, name = "Plugins Hypotheses", icon="mesh_tree_hypo.png")
    #, comment = "HypothesisForRemeshing" )

    monStudyBuilder=maStudy.NewBuilder()
    monStudyBuilder.NewCommand()
    newStudyIter=monStudyBuilder.NewObject(HypReMeshEntry)
    name = "MMG Parameters_%i" % self.num
    self.editor.setAttributeValue(newStudyIter, "AttributeName", name)
    data = self.getResumeData(separator=" ; ")
    self.editor.setAttributeValue(newStudyIter, "AttributeComment", data)
    
    if salome.sg.hasDesktop(): salome.sg.updateObjBrowser()
    self.num += 1
    if verbose: print(("save %s in Object Browser done:\n%s" % (name, data)))
    return True

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
    text+="HSize="+str(self.SP_HSize.value())+separator
    text+="MeshGradation="+str(self.SP_Gradation.value())+separator
    return str(text)

  def loadResumeData(self, hypothesis, separator="\n"):
    text=str(hypothesis)
    self.clean()
    for slig in reversed(text.split(separator)):
      lig=slig.strip()
      #print "load ResumeData",lig
      if lig=="": continue #skip blank lines
      if lig[0]=="#": break
      try:
        tit,value=lig.split("=")
        if tit=="RepairBeforeCompute": self.CB_RepairBeforeCompute.setChecked(value=="True")
        if tit=="SwapEdge": self.CB_SwapEdge.setChecked(value=="True")
        if tit=="InsertEdge": self.CB_InsertEdge.setChecked(value=="True")
        if tit=="MoveEdge": self.CB_MoveEdge.setChecked(value=="True")
        if tit=="GeometricalApproximation": self.SP_Geomapp.setProperty("value", float(value))
        if tit=="RidgeAngle": self.SP_Ridge.setProperty("value", float(value))
        if tit=="HSize": self.SP_HSize.setProperty("value", float(value))
        if tit=="MeshGradation": self.SP_Gradation.setProperty("value", float(value))
      except:
        QMessageBox.warning(self, "load MMG Hypothesis", "Problem on '"+lig+"'")

  def PBLoadPressed(self):
    """load last hypothesis saved in tail of file"""
    try:
      f=open(self.paramsFile,"r")
    except:
      QMessageBox.warning(self, "File", "Unable to open "+self.paramsFile)
      return
    try:
      text=f.read()
    except:
      QMessageBox.warning(self, "File", "Unable to read "+self.paramsFile)
      return
    f.close()
    self.loadResumeData(text, separator="\n")

  def PBLoadHypPressed(self):
    """load hypothesis saved in Object Browser"""
    #QMessageBox.warning(self, "load Object Browser MGSurfOpt hypothesis", "TODO")
    import salome
    from salome.kernel import studyedit
    from salome.smesh.smeshstudytools import SMeshStudyTools
    from salome.gui import helper as guihelper
    from omniORB import CORBA

    mySObject, myEntry = guihelper.getSObjectSelected()
    if CORBA.is_nil(mySObject) or mySObject==None:
      QMessageBox.critical(self, "Hypothese", "select an Object Browser MMG hypothesis")
      return
    
    text=mySObject.GetComment()
    
    self.loadResumeData(text, separator=" ; ")
    return
    
  def PBCancelPressed(self):
    self.close()

  def PBMeshFilePressed(self):
    fd = QFileDialog(self, "select an existing Mesh file", self.LE_MeshFile.text(), "Mesh-Files (*.mesh);;All Files (*)")
    if fd.exec_():
      infile = fd.selectedFiles()[0]
      self.LE_MeshFile.setText(infile)
      self.fichierIn=str(infile)
      self.values = Values(self.fichierIn, 0)
      self.MeshIn=""
      self.LE_MeshSmesh.setText("")
      self.__selectedMesh=None

  def setParamsFileName(self):
    fd = QFileDialog(self, "select a file", self.LE_ParamsFile.text(), "dat Files (*.dat);;All Files (*)")
    if fd.exec_():
      infile = fd.selectedFiles()[0]
      self.LE_ParamsFile.setText(infile)
      self.paramsFile=str(infile)

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

  def paramsFileNameChanged(self):
    self.paramsFile=self.LE_ParamsFile.text()

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

    self.values = None
    self.values = Values(myName, 0)
    #print "MeshSmeshNameChanged", myName
    self.MeshIn=myName
    self.LE_MeshSmesh.setText(myName)
    self.LE_MeshFile.setText("")
    self.fichierIn=""

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
    
    self.commande="mmgs_O3"

    deb=os.path.splitext(self.fichierIn)
    self.fichierOut=deb[0] + "_output.mesh"
    
    if self.CB_InsertEdge.isChecked()== False  : self.commande+=" -noinsert"
    if self.CB_SwapEdge.isChecked()== False  : self.commande+=" -noswap"
    if self.CB_MoveEdge.isChecked()== False  : self.commande+=" -nomove"
    if self.SP_Geomapp.value() != 0.01 : self.commande+=" -hausd %f"%self.SP_Geomapp.value()
    if self.SP_Ridge.value() != 45.0  : self.commande+=" -ar %f"%self.SP_Ridge.value()
    self.commande+=" -hsiz %f"   %self.SP_HSize.value()
    if self.SP_Gradation.value() != 1.3   : self.commande+=" -hgrad %f"  %self.SP_Gradation.value()

    self.commande+=' -in "'  + self.fichierIn +'"'
    self.commande+=' -out "' + self.fichierOut +'"'

    if verbose: print("INFO: MMG command:\n  %s" % self.commande)
    return True

  def clean(self):
    #no need: exlusives QRadioButton
    #self.RB_G.setChecked(False)
    #self.RB_U.setChecked(False)
    #self.RB_S.setChecked(False)
    #self.RB_2.setChecked(False)
    #self.RB_1.setChecked(False)
    #no need: exlusives QRadioButton
    #self.RB_Absolute.setChecked(False)
    if self.values is not None:
        self.SP_Geomapp.setProperty("value", self.values.geomapp)
        self.SP_Ridge.setProperty("value", self.values.ridge)
        self.SP_Gradation.setProperty("value", self.values.hgrad)
        self.SP_HSize.setProperty("value", self.values.hsize)
    else: # No file provided, default from MMG
        self.SP_Geomapp.setProperty("value", 0.01)
        self.SP_Ridge.setProperty("value", 45.0)
        self.SP_Gradation.setProperty("value", 1.3)
        self.SP_HSize.setProperty("value", 0.1)
    self.CB_RepairBeforeCompute.setChecked(True)
    self.CB_InsertEdge.setChecked(True)
    self.CB_MoveEdge.setChecked(True)
    self.CB_SwapEdge.setChecked(True)
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

# Copyright (C) 2012-2023 CEA/DEN, EDF R&D
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
CMAKE_MINIMUM_REQUIRED(VERSION 3.0 FATAL_ERROR)
INCLUDE(CMakeDependentOption)
PROJECT(MMGPLUGIN)
# upper case
STRING(TOUPPER ${PROJECT_NAME} PROJECT_NAME_UC)

SET(CONFIGURATION_ROOT_DIR $ENV{CONFIGURATION_ROOT_DIR} CACHE PATH "Path to the Salome CMake configuration files")
IF(EXISTS ${CONFIGURATION_ROOT_DIR})
  LIST(APPEND CMAKE_MODULE_PATH "${CONFIGURATION_ROOT_DIR}/cmake")
  INCLUDE(SalomeMacros NO_POLICY_SCOPE)
ELSE()
  MESSAGE(FATAL_ERROR "We absolutely need the Salome CMake configuration files, please define CONFIGURATION_ROOT_DIR !")
ENDIF()

# Versioning
# ===========
SALOME_SETUP_VERSION(1.0)

SET(SMESH_ROOT_DIR $ENV{SMESH_ROOT_DIR} CACHE PATH "Path to SMESH")
IF(NOT EXISTS ${SMESH_ROOT_DIR})
  MESSAGE(FATAL_ERROR "SMESH_ROOT_DIR environment variable is missing, please define SMESH_ROOT_DIR")
ENDIF()

# Python
FIND_PACKAGE(SalomePythonInterp REQUIRED)
FIND_PACKAGE(SalomePythonLibs REQUIRED)
FIND_PACKAGE(SalomePyQt5 REQUIRED)
INCLUDE(UsePyQt)

SET(_plugin_SCRIPTS
  compute_values.py
  mmgPlug_plugin.py
  myMmgPlugDialog.py
  myViewText.py
)

SET(_pyuic_FILES
    MyPlugDialog.ui
    ViewText.ui
)

# scripts / pyuic wrappings
PYQT_WRAP_UIC(_pyuic_SCRIPTS ${_pyuic_FILES} TARGET_NAME _target_name_pyuic)

# --- rules ---
SET(MMG_INSTALL_PLUGIN "plugins/mmgplugin")
SET(MMG_INSTALL_DOC    "doc")
SALOME_INSTALL_SCRIPTS("${_plugin_SCRIPTS}" "${MMG_INSTALL_PLUGIN}")
SALOME_INSTALL_SCRIPTS("${_pyuic_SCRIPTS}" "${MMG_INSTALL_PLUGIN}" TARGET_NAME _target_name_pyuic_py)
# add dependency of compiled py files on uic files in order
# to avoid races problems when compiling in parallel
ADD_DEPENDENCIES(${_target_name_pyuic_py} ${_target_name_pyuic})
# Install the CMake configuration files:
INSTALL(FILES "${PROJECT_SOURCE_DIR}/README.md" DESTINATION "${MMG_INSTALL_DOC}" )
SALOME_CONFIGURE_FILE(__init__.py __init__.py INSTALL "${MMG_INSTALL_PLUGIN}")
# check whether the plugin is already registered to SMESH plugins.
# sadly this is not available as a macro from the SMESH installation
SET(SALOME_SMESH_INSTALL_PLUGINS share/salome/plugins/smesh CACHE PATH
    "Install path: SALOME SMESH plugins")
SET(SMESH_PLUGINS_FILE ${SMESH_ROOT_DIR}/${SALOME_SMESH_INSTALL_PLUGINS}/smesh_plugins.py)
FILE(READ ${SMESH_PLUGINS_FILE} SMESH_PLUGINS_FILE_CONTENTS)
STRING(FIND  "${SMESH_PLUGINS_FILE_CONTENTS}" "mmgplugin.mmgPlug_plugin" MMGPLUGIN)
IF (MMGPLUGIN EQUAL -1)
   FILE(APPEND ${SMESH_PLUGINS_FILE} "\n# MMG Plugin\n\
try:\n\
  from mmgplugin.mmgPlug_plugin import Mmg\n\
  salome_pluginsmanager.AddFunction('ReMesh with MMG', 'Run MMG', Mmg)\n\
except Exception as e:\n\
  salome_pluginsmanager.logger.info('ERROR: MMG plug-in is unavailable: {}'.format(e))\n\
  pass\n")
ENDIF()

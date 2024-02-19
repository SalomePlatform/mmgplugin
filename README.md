mmgplugin
======

<p align="center">
  <img src="https://github.com/SalomePlatform/mmgplugin/assets/52162083/af337c45-1e97-4869-8e03-8d277baf319c" alt="bool" width="400" />
  <img src="https://github.com/SalomePlatform/mmgplugin/assets/52162083/e9160a2b-03b1-4e1a-a187-60d8dbb9a96d" alt="smesh" width="400" />
</p>


For SALOMEs SMESH module -- which provides an open-source meshing framework for  numerical simulations -- the integration of mesh adaptation capabilities is paramount to enhancing its usability and effectiveness. This mmgplugin, leveraging the powerful MMG library,  brings advanced mesh adaptation cpabilities to SALOME's SMESH module. By seamlessly integrating MMG's robust mesh adaptation algorithms into SALOME, users gain access to state-of-the-art techniques for mesh optimization and refinement. This integration should empower engineers, scientists, and researchers to tackle increasingly complex simulation challenges with confidence, knowing that they have the tools necessary to generate high-quality meshes tailored to their specific needs. 

Local Tests
=======


To try the plugin locally, follow these steps:

1. Open the file located at `$SMESH_ROOT_DIR/share/salome/plugins/smesh/smesh_plugins.py`.

2. Add the following code to the end of the file:
   
```
   try:
	   from mmgplugin.mmgPlug_plugin import Mmg
	   salome_pluginsmanager.AddFunction('ReMesh with MMG', 'Run MMG', Mmg)
   except Exception as e:
	   salome_pluginsmanager.logger.info('ERROR: MMG plug-in is unavailable: {}'.format(e))
	   pass
```
3. Compilation
```
cd $SMESH_ROOT_DIR/share/salome/plugins/smesh/mmgplugin
make
```

5. Dependencies:
```
$SALOME_ROOT_DIR/salome context
pip install meshio
cd $SALOME_ROOT_DIR/BINARIES[...]
wget https://github.com/MmgTools/mmg/releases/download/v5.6.0/mmg-5.6.0-Linux-4.4.0-170-generic-appli.tar.gz
tar -xvf mmg-5.6.0-Linux-4.4.0-170-generic-appli.tar.gz
mv bin mmg
export PATH=$PWD/mmg:$PATH
```
You can test if mmg is correctly installed by running `mmgs_O3 -h`

How to use ?
=======
1. run the command 'make' (this generates the ui python file)
2. start salome
3. find the plugin with the other SMESH plugins

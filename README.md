mmgplugin
======
MMG (Mesh Adaptation Kernel) Interface for SALOME

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
```
Download the mmg binaries (link)[https://github.com/MmgTools/mmg/releases/download/v5.6.0/mmg-5.6.0-Darwin-17.6.0-appli.tar.gz]
untar it and put the path of the binaries in your path vraiable

How to use ?
=======
1. run the command 'make' (this generates the ui python file)
2. start salome
3. find the plugin with the other SMESH plugins

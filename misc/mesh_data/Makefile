PY_FILES := $(wildcard archive_meshes/*.py)
MESH_FILES := $(PY_FILES:.py=.mesh)

all:
	mkdir -p archive_meshes
	~/SALOME-9.11.0-native-UB22.04-SRC/salome shell -l -script MakeMesh.py

clean:
	rm $(MESH_FILES)

.PHONY: all clean

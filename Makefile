UI_FILE=MmgsPlugDialog.ui
PY_FILE=MyPlugDialog_ui.py

all: $(PY_FILE)

$(PY_FILE): $(UI_FILE)
	pyuic5 $< -o $@

clean:
	rm -f $(PY_FILE)

.PHONY: all clean


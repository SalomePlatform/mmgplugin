OUTPUT_FILES := $(wildcard **/*_output.*)
all:
	./gen.sh

delete_gen:
	rm -rf gen_surface

clean:
	if [ -n "$(OUTPUT_FILES)" ]; then rm $(OUTPUT_FILES); fi
	if [ -e "logs.txt" ]; then rm logs.txt; fi


.PHONY: all clean

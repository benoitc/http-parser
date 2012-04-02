# This file is renamed to "Makefile.ext" in release tarballs so that
# setup.py won't try to run it.  If you want setup.py to run "make"
# automatically, rename it back to "Makefile".

all: http_parser/parser.c

http_parser/parser.c: http_parser/parser.pyx
	cython -o http_parser.parser.c http_parser/parser.pyx
	mv http_parser.parser.c http_parser/parser.c

clean:
	rm -f http_parser/parser.c


.PHONY: clean all

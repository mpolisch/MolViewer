CC=clang
CFLAGS= -Wall -std=c99 -pedantic

all: makeMolecule libmol.so _molecule.so

clean:
	rm -f *.o *.so molecule.py molecule_wrap.c libmol.so _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so -lm

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I /usr/include/python3.7m -o molecule_wrap.o

_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o -shared -L -l libmol.so -L /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -l python3.7m -dynamiclib -o _molecule.so

makeMolecule: molecule.i
	swig3.0 -python molecule.i

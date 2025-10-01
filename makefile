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
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I/usr/include/python3.10 -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) molecule_wrap.o -shared -L. -lmol -L/usr/lib/python3.10/config-3.10-x86_64-linux-gnu -L/usr/lib/x86_64-linux-gnu -lpython3.10 -o _molecule.so

makeMolecule: molecule.i
	swig -python molecule.i

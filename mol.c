#ifndef LIBS_H

#include <stdlib.h>
#include "mol.h"
#include <math.h>
#include <string.h>
#define M_PI 3.14159265358979323846 // Pi is needed for converting degrees to rads in matrix rotations

#endif

/*
atomset sets the data given into the atom structure
*/

void atomset( atom *atom, char element[3], double *x, double *y, double *z ){

	if(element[0] == '\0'){    //checks for an empty atom, returns if empty
		return;
	}

	strcpy(atom->element, element); 
	atom->x = *x;
	atom->y = *y;
	atom->z = *z;
}

/*
atomget gets the data from atom and copies it into separate variables
*/

void atomget( atom *atom, char element[3], double *x, double *y, double *z ){

	if(atom->element[0] == '\0'){     //checks for an empty atom, returns if empty
		return;
	}

	strcpy(element, atom->element);
	*x = atom->x;
	*y = atom->y;
	*z = atom->z;
}

/*
bondset gets the atoms passed into the function and sets the atoms in the bond
*/

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs ){
	bond->atoms = *atoms;
	bond->a1 = *a1;
	bond->a2 = *a2;

	bond->epairs = *epairs;
	compute_coords(bond);

}

void compute_coords( bond *bond ){

	bond->x1 = bond->atoms[bond->a1].x;
	bond->x2 = bond->atoms[bond->a2].x;

	bond->y1 = bond->atoms[bond->a1].y;
	bond->y2 = bond->atoms[bond->a2].y;

	bond->z = (bond->atoms[bond->a2].z + bond->atoms[bond->a1].z) / 2;

	bond->len = pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2);

	bond->len = sqrt(bond->len);

	bond->dx = (bond->x2 - bond->x1) / bond->len;
	bond->dy = (bond->y2 - bond->y1) / bond->len;

}

/*
bondget gets the atoms in the bond, as well as the pair and copies them into separate variables
*/

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs ){

	*a1 = bond->a1;
	*a2 = bond->a2;
	*atoms = bond->atoms;
	*epairs = bond->epairs;

}

/*
molmalloc dynamically allocates memory for a molecule data type
given the maximum bonds possible as well as the maximum atoms possible
it returns the molecule
*/

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){

	molecule * temp = malloc(sizeof(molecule)); //allocates memory needed for a molecule

	temp->atom_no = 0;
	temp->atom_max = atom_max;

	temp->atoms = malloc(sizeof(atom)*atom_max);     //allocates memory for the maximum amount of atoms possible
	temp->atom_ptrs = malloc(sizeof(atom)*atom_max); //allocates memory for the maximum amount of pointers to atoms possible

	temp->bond_max = bond_max;
	temp->bond_no = 0;

	temp->bonds = malloc(sizeof(bond)*bond_max);     //allocates memory for the maximum amount of bonds possible 
	temp->bond_ptrs = malloc(sizeof(bond)*bond_max); //allocates memory for the maximum amount of pointers to bonds possible

	return temp;

}

/*
molcopy copies the elements in a molecule into a new copy of it, returning the molecule
*/

molecule *molcopy( molecule *src ){

	molecule * temp = molmalloc(src->atom_max, src->bond_max);  //allocates memory for the copy

	for(int i = 0; i < src->atom_no; i++){     //loop to append all the atoms into the new molecule
		molappend_atom(temp, &src->atoms[i]);
	}

	for(int i = 0; i < src->bond_no; i++){
		molappend_bond(temp, &src->bonds[i]);  //loop to append all the bonds into the new molecules
	}

	return temp;

}

/*
molefree frees all the allocated memory in a molecule
*/

void molfree( molecule *ptr ){

	free(ptr->atoms);
	free(ptr->atom_ptrs);
	free(ptr->bonds);
	free(ptr->bond_ptrs);
	free(ptr);

}

/*
molappend_atom appends an atom into a molecule, reallocating memory if needed
*/

void molappend_atom( molecule *molecule, atom *atom ){

	if(molecule->atom_no == molecule->atom_max){    //checks if the atoms have reached the maximum

		if(molecule->atom_max == 0){     //checks if there are no atoms in the array

			molecule->atom_max++; 

			molecule->atoms = realloc(molecule->atoms, sizeof(struct atom)); //reallocates memory for a single atom
			if(molecule->atoms == NULL){
				exit(0);
			}
			molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*)); //reallocates memory for a single pointer
			if(molecule->atom_ptrs == NULL){
				exit(0);
			}

		} else{

			molecule->atom_max = molecule->atom_max*2;  //if the maximum is not empty, doubles the maximum

			molecule->atoms = realloc(molecule->atoms, sizeof(struct atom)*molecule->atom_max);  //reallocates memory for all the atoms
			if(molecule->atoms == NULL){
				exit(0);
			}
			molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*)*molecule->atom_max); //reallocates memory for all the pointers
			if(molecule->atom_ptrs == NULL){
				exit(0);
			}
		}

		for(int i = 0; i < molecule->atom_no; i++){   //repoints the atom_ptrs to the new memory addresses of the atoms
			molecule->atom_ptrs[i] = &molecule->atoms[i];
		}

	}

	molecule->atoms[molecule->atom_no] = *(atom); //appends the atom to the end of the array
	molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no]; //appends the pointer to the end of the array
	molecule->atom_no++;  //increases the number of atoms

}

/*
molappend_bond appends a bond to the molecule, reallocating memory if needed
*/

void molappend_bond( molecule *molecule, bond *bond ){

	if(molecule->bond_no == molecule->bond_max){  //checks if the bonds have reached the maximum
		
		if(molecule->bond_max == 0){   //checks if there are no bonds in the array

			molecule->bond_max++;

			molecule->bonds = realloc(molecule->bonds, sizeof(struct bond));   //reallocates memory for a single bond
			if(molecule->bonds == NULL){
				molfree(molecule);
				exit(0);
			}
			molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)); //reallocates memory for a single pointer
			if(molecule->bond_ptrs == NULL){
				molfree(molecule);
				exit(0);
			}
		} else{

			molecule->bond_max = molecule->bond_max*2; //if max not empty, double the max
			
			molecule->bonds = realloc(molecule->bonds, sizeof(struct bond)*molecule->bond_max); //reallocates memory for all the bonds
			if(molecule->bonds == NULL){
				molfree(molecule);
				exit(0);
			}
			molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)*molecule->bond_max); //reallocates memory for all the pointers
			if(molecule->bond_ptrs == NULL){
				molfree(molecule);
				exit(0);
			}
		
		}

		for(int i = 0; i < molecule->bond_no; i++){   //repoints the memory addresses of atom_ptrs to the new addresses after realloc
			molecule->bond_ptrs[i] = &molecule->bonds[i];
		}

	}

	molecule->bonds[molecule->bond_no] = *(bond); //appends the bond
	molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no]; //appends the pointer
	molecule->bond_no++;

}

/*
molsort sorts the array of atom_ptrs based on increasing z values
*/

void molsort( molecule *molecule ){

	qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom*), compare_atoms);
	qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond*), bond_comp);

}

/*
compare_atoms is a helper function for molsort
it compares two z values and returns the difference
*/

int compare_atoms(const void * a, const void * b){

	return ( (*(atom **)a)->z - (*(atom**)b)->z );

}

/*
compare_bonds is a helper function for molsort
it averages the z values of the two atoms in the bond and then returns the difference between 2 atoms
*/

int bond_comp( const void *a, const void *b ){

	return ((*(bond **)a)->z - (*(bond **)b)->z);

}

/*
xrotation builds a matrix that will eventually allow for a molecule to move in 3D space
*/

void xrotation( xform_matrix xform_matrix, unsigned short deg ){

	double rad = deg * (M_PI / 180.0);

	xform_matrix[0][0] = 1;
	xform_matrix[0][1] = 0;
	xform_matrix[0][2] = 0;
	xform_matrix[1][0] = 0;
	xform_matrix[1][1] = cos(rad);
	xform_matrix[1][2] = -(sin(rad));
	xform_matrix[2][0] = 0;
	xform_matrix[2][1] = sin(rad);
	xform_matrix[2][2] = cos(rad);

}

/*
yrotation builds a matrix that will eventually allow for a molecule to move in 3D space
*/

void yrotation( xform_matrix xform_matrix, unsigned short deg ){

	double rad = deg * (M_PI / 180.0);

	xform_matrix[0][0] = cos(rad);
	xform_matrix[0][1] = 0;
	xform_matrix[0][2] = sin(rad);
	xform_matrix[1][0] = 0;
	xform_matrix[1][1] = 1;
	xform_matrix[1][2] = 0;
	xform_matrix[2][0] = -(sin(rad));
	xform_matrix[2][1] = 0;
	xform_matrix[2][2] = cos(rad);

}

/*
zrotation builds a matrix that will eventually allow for a molecule to move in 3D space
*/

void zrotation( xform_matrix xform_matrix, unsigned short deg ){

	double rad = deg * (M_PI / 180.0);

	xform_matrix[0][0] = cos(rad);
	xform_matrix[0][1] = -(sin(rad));
	xform_matrix[0][2] = 0;
	xform_matrix[1][0] = sin(rad);
	xform_matrix[1][1] = cos(rad);
	xform_matrix[1][2] = 0;
	xform_matrix[2][0] = 0;
	xform_matrix[2][1] = 0;
	xform_matrix[2][2] = 1;

}

/*
mol_xform performs matrix multipication for each atom and updates the x y and z coordinates for each atom
*/

void mol_xform( molecule *molecule, xform_matrix matrix ){

	for (int i = 0; i < molecule->atom_no; i++){

		double rotation_x = matrix[0][0]*molecule->atoms[i].x + matrix[0][1]*molecule->atoms[i].y + matrix[0][2]*molecule->atoms[i].z;
		double rotation_y = matrix[1][0]*molecule->atoms[i].x + matrix[1][1]*molecule->atoms[i].y + matrix[1][2]*molecule->atoms[i].z;
		double rotation_z = matrix[2][0]*molecule->atoms[i].x + matrix[2][1]*molecule->atoms[i].y + matrix[2][2]*molecule->atoms[i].z;

		molecule->atoms[i].x = rotation_x;
		molecule->atoms[i].y = rotation_y;
		molecule->atoms[i].z = rotation_z;

	}
	molecule->bonds->atoms = molecule->atoms;
        for(int i = 0; i < molecule->bond_no; i++){
		compute_coords(molecule->bond_ptrs[i]);
        }
}

import molecule;

header = """<svg version="1.1" width="1000" height="1000"
                    xmlns="http://www.w3.org/2000/svg">""";

footer = """</svg>""";

offsetx = 500;
offsety = 500;

#Atom class, extends atom struct from c-code

class Atom:

    def __init__(self, c_atom): #constructor to set all atoms
        self.atom = c_atom;
        self.z = c_atom.z;

    def __str__(self): #method prints a string with atom data in order to debug
        print(self.atom.element + " " + self.atom.x + " " + self.atom.y + " " + self.atom.z);

    def svg (self): #method returns a string that contains formatting to create an svg file
        
        if self.atom.element in element_name:
            string = ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' %((self.atom.x * 100) + offsetx, (self.atom.y * 100) + offsety, radius[self.atom.element], element_name[self.atom.element]);
        else:
            string = ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' %((self.atom.x * 100) + offsetx, (self.atom.y * 100) + offsety, 30, "element");

        return string;

#Bond class, extends bond struct from c-code

class Bond:

    def __init__(self, c_bond): #constructor to set all bonds
        self.bond = c_bond;
        self.z = c_bond.z;

    def __str__(self): #method prints a string with bond data in order to debug
        print(self.bond.x1 + " " + self.bond.x2 + " " + self.bond.y1 + " " + self.bond.y2 + " " + self.bond.len + " " + self.bond.dx + " " + self.bond.dy);

    def svg (self): #method returns a string that contains formatting to create an svg file
        string = ' <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' %(((self.bond.x1 * 100) + offsetx) - self.bond.dy * 10, ((self.bond.y1 * 100) + offsety) + (self.bond.dx * 10.0), ((self.bond.x1 * 100) + offsetx) + (self.bond.dy * 10.0), ((self.bond.y1 * 100) + offsety) - (self.bond.dx * 10), ((self.bond.x2 * 100) + offsetx) + (self.bond.dy * 10.0), ((self.bond.y2 * 100) + offsety) - (self.bond.dx * 10.0), ((self.bond.x2 * 100) + offsetx) - (self.bond.dy * 10.0), ((self.bond.y2 * 100) + offsety) + (self.bond.dx*10));
        return(string);

#Molecule class, subclass of molecule struct from c-code

class Molecule(molecule.molecule):

    def __str__(self): #method prints a string with molecule data in order to debug
        print("atom no: " + self.atom_no + "bond no: "  + self.bond_no + "atom max: "  + self.atom_max + "bonx max: " + self.bond_max);

    def svg(self): #method returns a complete svg string which is made using the svg methods from Atom class and Bond classs
        atom = [];
        bond = [];
        ordered = [];
        for i in range(self.atom_no): #loops for all atoms
            atom.append(Atom(self.get_atom(i))); #adds atom to list
        for i in range(self.bond_no): #loops for all bonds
            bond.append(Bond(self.get_bond(i))); #adds bond to list
        ordered = [*atom, *bond]; #concatenates both bond and atom lists
        ordered.sort(key=lambda x: x.z, reverse=False); #sorts the list based on the z values of atoms and bonds
        theHead = header; 
        for i in range(self.atom_no + self.bond_no): #combines all svg data from each atom and bond
           theHead += (ordered[i].svg());
        theHead += footer;
        return (theHead);

    def parse(self, file_obj): #method parses data from an sdf file either recieved locally or from a webserver
        for i in range(3): #loops for first 3 lines to skip them
        	line = file_obj.readline();
        sdfData = [];
        no_list = [];
        if(isinstance(line, bytes)): #checks if the data is encoded from a webserver or not
            sdfData.append(file_obj.readline().decode('utf-8')); #appends first line to list
            no_list = sdfData[0].split();
            for i in range(1, int(no_list[0]) + 1): #loops for number of atoms
                sdfData.append(file_obj.readline().decode('utf-8')); #adds atom data to list
            for i in range(1 + int(no_list[0]), 1 + int(no_list[0]) +   int(no_list[1])): #loops for number of bonds
                sdfData.append(file_obj.readline().decode('utf-8')); #adds bond data to list
        else:
            sdfData.append(file_obj.readline()); #does the same as the above code, but without decoding any of the data
            no_list = sdfData[0].split();
            for i in range(1, int(no_list[0]) + 1):
                sdfData.append(file_obj.readline());
            for i in range(1 + int(no_list[0]), 1 + int(no_list[0]) +   int(no_list[1])):
                sdfData.append(file_obj.readline());
        for i in range(1, int(no_list[0]) + 1): #loops for all atoms
            atom_data = sdfData[i].split(); #splits each atom string into individual strings of data
            self.append_atom(atom_data[3], float(atom_data[0]), float(atom_data[1]), float(atom_data[2])); #appends data to molecule
        for i in range(1 + int(no_list[0]), 1 + int(no_list[0]) + int(no_list[1])): #loops for all bonds
            bond_data = sdfData[i].split(); #splits each bond string into individual strings of data
            self.append_bond(int(bond_data[0]) - 1, int(bond_data[1]) - 1, int(bond_data[2])); #appends data to molecule

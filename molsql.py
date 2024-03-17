import MolDisplay;
import sqlite3;
import os;

#Database class for creating an SQL database for molecules

class Database:

    def __init__(self, reset=False): #constructor creates database
        if reset == True: #deletes database if reset is set True
            os.remove('molecule.db'); 
        self.conn = sqlite3.connect('molecule.db'); #creates database, establishes connection
    def create_tables(self):
        cur = self.conn.cursor(); 
        cur.execute("""CREATE TABLE IF NOT EXISTS Elements
                        (ELEMENT_NO INTEGER NOT NULL,
                         ELEMENT_CODE VARCHAR(3) NOT NULL PRIMARY KEY,
                         ELEMENT_NAME VARCHAR(32) NOT NULL,
                         COLOUR1 CHAR(6) NOT NULL,
                         COLOUR2 CHAR(6) NOT NULL,
                         COLOUR3 CHAR(6) NOT NULL,
                         RADIUS DECIMAL(3) NOT NULL)"""); #creates Elements table
        cur.execute("""CREATE TABLE IF NOT EXISTS Atoms
                        (ATOM_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                         ELEMENT_CODE VARCHAR(3) NOT NULL,
                         X DECIMAL(7, 4) NOT NULL,
                         Y DECIMAL(7, 4) NOT NULL,
                         Z DECIMAL(7, 4) NOT NULL,
                         FOREIGN KEY(ELEMENT_CODE) REFERENCES Elements (ELEMENT_CODE))"""); #creates Atoms table
        cur.execute("""CREATE TABLE IF NOT EXISTS Bonds
                        (BOND_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                         A1 INTEGER NOT NULL,
                         A2 INTEGER NOT NULL,
                         EPAIRS INTEGER NOT NULL)"""); #creates Bonds table
        cur.execute("""CREATE TABLE IF NOT EXISTS Molecules
                        (MOLECULE_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                         NAME TEXT NOT NULL UNIQUE)"""); #creates Molecule table
        cur.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                        (MOLECULE_ID INTEGER NOT NULL,
                         ATOM_ID INTEGER NOT NULL,
                         PRIMARY KEY(MOLECULE_ID, ATOM_ID)
                         FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID), 
                         FOREIGN KEY(ATOM_ID) REFERENCES Atoms(ATOM_ID))"""); #creates MoleculeAtom table
        cur.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                        (MOLECULE_ID INTEGER NOT NULL,
                         BOND_ID INTEGER NOT NULL,
                         PRIMARY KEY(MOLECULE_ID, BOND_ID)
                         FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                         FOREIGN KEY(BOND_ID) REFERENCES Bonds(BOND_ID))"""); #creates MoleculeBond table
        self.conn.commit(); #adds tables to file

    def __setitem__ (self, table, values): #helper method for adding data to tables
        cur = self.conn.cursor();
        
        if table == 'Elements': #determines what table has been passed, adds values accordingly
            cur.execute("INSERT INTO Elements VALUES(?, ?, ?, ?, ?, ?, ?)", values);
        elif table == 'Atoms':
            cur.execute("INSERT INTO Atoms VALUES(?, ?, ?, ?, ?)", values);
        elif table == 'Bonds':
            cur.execute("INSERT INTO Bonds VALUES(?, ?, ?, ?)", values);
        elif table == 'Molecules':
            cur.execute("INSERT INTO Molecules VALUES(?, ?)", values);
        elif table == 'MoleculeAtom':
            cur.execute("INSERT INTO MoleculeAtom VALUES(?, ?)", values);
        elif table == 'MoleculeBond':
            cur.execute("INSERT INTO MoleculeBond VALUES(?, ?)", values);
        self.conn.commit();

    def add_atom(self, molname, atom): #method adds an atom to the Atoms table, and connects it with the Molecules table through the MoleculeAtom table
        cur = self.conn.cursor();
        self['Atoms'] = (None, atom.element, atom.x, atom.y, atom.z); #adds data to table
        cur.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME= ?", (molname,)); #finds moleculeid based on molecule name passed into method
        molid = cur.fetchone()[0];
        cur.execute("SELECT ATOM_ID FROM Atoms WHERE ELEMENT_CODE = ? AND X = ? AND Y = ? AND Z = ?", (atom.element, atom.x, atom.y, atom.z)); #finds atomid based on atom data passed into method
        atomid = cur.fetchone()[0];
        self['MoleculeAtom'] = (molid, atomid); #adds data to MoleculeAtom table
        self.conn.commit();
    def add_bond(self, molname, bond): #method adds a bond to the Bonds table, and connects it with the Molecules table through the MoleculeBond table
        cur = self.conn.cursor();
        self['Bonds'] = (None, bond.a1, bond.a2, bond.epairs); #adds data to table
        cur.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,)); #finds moleculeid based on molecule name passed into method
        molid = cur.fetchone()[0];
        cur.execute("SELECT BOND_ID FROM Bonds WHERE A1 = ? AND A2 = ? AND EPAIRS = ?", (bond.a1, bond.a2, bond.epairs)); #finds bondid based on bond data passed into method
        bondid = cur.fetchone()[0];
        self['MoleculeBond'] = (molid, bondid); #adds data to MoleculeBond table
        self.conn.commit();
    def add_molecule(self, name, fp): #method adds a molecule to the database
        cur = self.conn.cursor();
        mol = MolDisplay.Molecule(); #creates a new molecule object
        mol.parse(fp); #adds atoms & bonds into structure
        self['Molecules'] = (None, name); #adds Molecule to database
        self.conn.commit();
        for i in range(mol.atom_no): #loops for all atoms
            atom = mol.get_atom(i); #gets the atom
            self.add_atom(name, atom); #adds atom to database
        for i in range(mol.bond_no): #loops for all bonds
            bond = mol.get_bond(i); #gets bond
            self.add_bond(name, bond); #adds bond to database
        self.conn.commit();
    def load_mol( self, name ): #method loads molecule struct based on molecule name passed in, creates the molecule and returns it
        cur = self.conn.cursor();
        mol = MolDisplay.Molecule(); #new molecule object
        atomList = cur.execute("SELECT * FROM Atoms, MoleculeAtom, Molecules WHERE MoleculeAtom.ATOM_ID = Atoms.ATOM_ID AND MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID AND Molecules.NAME = ?", (name,)).fetchall(); #obtains list of atom data from molecule
        for i in atomList: #loops through list, and appends atoms to the molecule
            mol.append_atom(i[1], i[2], i[3], i[4]);
        bondList = cur.execute("SELECT * FROM Bonds, MoleculeBond, Molecules WHERE MoleculeBond.BOND_ID = Bonds.BOND_ID AND MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID AND Molecules.NAME = ?", (name,)).fetchall(); #obtains list of bond data from molecule
        for i in bondList: #loops through list, and appends bonds to the molecule
            mol.append_bond(i[1], i[2], i[3]);
        return mol;
    def radius(self): #method creates and returns a dictionary of all radius values for each element based on the element code
        cur = self.conn.cursor();
        res = cur.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements"); #retrieves all radius's and element codes
        radiusList = res.fetchall(); 
        radiusDict = {}; 
        for i in radiusList: #turns list into dictionary
            radiusDict[i[0]] = i[1];
        return radiusDict;
    def element_name(self): #method creates and returns a dictionary of all element names for each element based on the element code
        cur = self.conn.cursor();
        res = cur.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements"); #retrieves all element names and codes
        elementList = res.fetchall();
        elementDict = {};
        for i in elementList: #turns returned list into dictionary
            elementDict[i[0]] = i[1];
        return elementDict;
    def radial_gradients( self ): #method creates a string of all radialGradient values and returns the svg string associated
        cur = self.conn.cursor();
        res = cur.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements"); #retrieves all values needed for gradient
        element = res.fetchall();
        radialGradientSVG = '';
        if len(element) != 0:
            for i in element: #loops for all elements
                radialGradientSVG += """
                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                    <stop offset="0%%" stop-color="#%s"/>
                    <stop offset="50%%" stop-color="#%s"/>
                    <stop offset="100%%" stop-color="#%s"/>
                </radialGradient>""" %(i[0], i[1], i[2], i[3]); #appends to string
        else:
            radialGradientSVG += """
                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                    <stop offset="0%%" stop-color="#%s"/>
                    <stop offset="50%%" stop-color="#%s"/>
                    <stop offset="100%%" stop-color="#%s"/>
                </radialGradient>""" %("element", "##00FF00", "#FF0000", "#FFFF00");
        return radialGradientSVG;

if __name__ == "__main__":
    db = Database(reset=True);
    db.create_tables();

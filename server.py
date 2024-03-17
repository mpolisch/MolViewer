import sys;
import MolDisplay;
import molecule;
import molsql;
import sqlite3;
import os;
import json;
from http.server import HTTPServer, BaseHTTPRequestHandler;
from urllib.parse import urlparse, parse_qs;

class MyHandler( BaseHTTPRequestHandler ):

    xAngle = 0;

    yAngle = 0;

    zAngle = 0;

    def do_GET(self):
        
        query = urlparse(self.path).query
        path = urlparse(self.path).path

        if path == "/":
            
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len(home_page) );
            self.end_headers();
            self.wfile.write( bytes( home_page, "utf-8" ) );

        elif path == "/getelements":

            db = molsql.Database(reset = False);
            cur = db.conn.cursor();
            
            res = cur.execute("SELECT ELEMENT_NAME FROM Elements");
            elements = res.fetchall();

            elementsJSON = json.dumps(elements).encode();
            self.send_response(200);
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", "application/json");
            self.end_headers();

            self.wfile.write(elementsJSON);
            
        elif path == "/getsvg":

            db = molsql.Database(reset = False);

            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();

            molName = parse_qs(query);

            mol = db.load_mol(molName['moleculeName'][0]);

            if (MyHandler.xAngle != 0):
                mx = molecule.mx_wrapper( MyHandler.xAngle, 0, 0);
                mol.xform( mx.xform_matrix );
            if (MyHandler.yAngle != 0):
                mx = molecule.mx_wrapper(0, MyHandler.yAngle, 0);
                mol.xform( mx.xform_matrix );
            if (MyHandler.zAngle != 0):
                mx = molecule.mx_wrapper(0, 0, MyHandler.zAngle);
                mol.xform( mx.xform_matrix );

            mol.sort();

            svgFile = mol.svg();

            self.send_response(200);
            self.send_header("Content-type", "text/plain");
            self.send_header("Content-length", len(svgFile));
            self.end_headers();

            self.wfile.write(bytes(svgFile, "utf-8"));

        elif path == "/getmolecules":

            db = molsql.Database(reset = False);
            cur = db.conn.cursor();
            
            res = cur.execute("SELECT * FROM Molecules");
            molecules = res.fetchall();

            moleculeDict = {};

            atomNo = 0;
            bondNo = 0;

            for i in molecules:
              res = cur.execute("SELECT ATOM_ID FROM MoleculeAtom WHERE MoleculeAtom.MOLECULE_ID = ?", (i[0],));
              atoms = res.fetchall();
              atomNo = len(atoms);
              res = cur.execute("SELECT BOND_ID FROM MoleculeBond WHERE MoleculeBond.MOLECULE_ID = ?", (i[0],));
              bonds = res.fetchall();
              bondNo = len(bonds);
              moleculeDict[i[1]] = [atomNo, bondNo];

            moleculeDictJSON = json.dumps(moleculeDict).encode();
            self.send_response(200);
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", "application/json");
            self.end_headers();

            self.wfile.write(moleculeDictJSON);

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

    def do_POST(self):

        if self.path == "/uploadsuccess":

            for i in range(3):
                self.rfile.readline();

            molName = self.rfile.readline().decode('utf-8');

            molName = molName[:len(molName)-2];

            for i in range(4):
                self.rfile.readline();

            db = molsql.Database(reset = False);

            cur = db.conn.cursor();

            res = cur.execute("SELECT NAME FROM Molecules");
            molecules = res.fetchall();

            unique = 1;

            for i in molecules: 
                temp = "('" + molName + "',)";
                if temp == str(i):
                    unique = 0;
            if unique == 1:
                db.add_molecule(molName, self.rfile);
                self.send_response( 200 ); # OK
                self.end_headers();
            else:
                self.send_response( 404 );
                self.end_headers();

        elif self.path == "/removeelement":

            content_len = int(self.headers.get('Content-Length'));
            post_body = self.rfile.read(content_len).decode("utf-8");
            elementName = json.loads(post_body);

            elementString = str(elementName['elementName'])[2:];
            elementString = elementString[:-2];

            db = molsql.Database(reset = False);

            cur = db.conn.cursor();
            cur.execute("DELETE FROM Elements WHERE Elements.ELEMENT_NAME = ?", (elementString,));
            db.conn.commit();

            self.send_response(200);
            self.send_header('Content-type', 'application/json');
            self.end_headers();
            response = {'status': 'success'};
            self.wfile.write(json.dumps(response).encode());

        elif self.path == "/addelement":

            content_len = int(self.headers.get('Content-Length'));
            post_body = self.rfile.read(content_len).decode("utf-8");
            elementData = json.loads(post_body);
            
            db = molsql.Database(reset = False);

            elements = db.element_name();
            unique = 1;

            for i in elements:
                if elements[i] == elementData['elementName']:
                    unique = 0;

            if unique == 1:

                db['Elements'] = (elementData['elementNumber'], elementData['elementCode'].upper(), elementData['elementName'].capitalize(), elementData['elementColor1'][1:].upper(), elementData['elementColor2'][1:].upper(), elementData['elementColor3'][1:].upper(), elementData['elementRadius']);

                self.send_response(200);
                self.send_header('Content-type', 'application/json');
                self.end_headers();
                response = {'status': 'success'};
                self.wfile.write(json.dumps(response).encode());
            else:
                self.send_response( 404 );
                self.end_headers();

        elif self.path == "/rotate":

            content_len = int(self.headers.get('Content-Length'));
            post_body = self.rfile.read(content_len).decode("utf-8");
            coords = json.loads(post_body);

            db = molsql.Database(reset = False);
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();
            
            mol = db.load_mol(coords['moleculeName']);

            xCoord = int(coords['xCoord']) + 10;
            yCoord = int(coords['yCoord']) + 10;
            zCoord = int(coords['zCoord']) + 10;

            MyHandler.xAngle = xCoord % 360;
            MyHandler.yAngle = yCoord % 360;
            MyHandler.zAngle = zCoord % 360;

            self.send_response(200);
            self.end_headers();

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8"));

with open("homepage.html", "r") as f:
  home_page = f.read()

httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
httpd.serve_forever();


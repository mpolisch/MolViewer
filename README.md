# MolViewer - Molecular Visualization Web Application

A web-based molecular visualization tool built with C, Python, and JavaScript that allows users to upload, view, and interact with 3D molecular structures.

## Features

- **3D Molecular Visualization**: Interactive SVG-based molecular structure display
- **File Upload**: Support for SDF (Structure Data Format) molecular files
- **Element Management**: Add and remove chemical elements with custom properties
- **3D Rotation**: Real-time molecular rotation with X, Y, Z axis controls
- **Database Storage**: SQLite database for persistent molecular and element data
- **Web Interface**: User-friendly tabbed interface for all features

## Architecture

The project consists of several key components:

- **C Library (`mol.c`, `mol.h`)**: Core molecular data structures and algorithms
- **Python Bindings (`molecule.i`)**: SWIG-generated Python interface to C library
- **Display Engine (`MolDisplay.py`)**: Python classes for SVG visualization
- **Database Layer (`molsql.py`)**: SQLite database management
- **Web Server (`server.py`)**: HTTP server handling API requests
- **Frontend (`homepage.html`)**: Interactive web interface

## Prerequisites

Before running MolViewer, ensure you have the following installed:

- **Python 3.10+**
- **clang** (C compiler)
- **swig** (for generating Python bindings)
- **python3-dev** (Python development headers)

### Installing Dependencies on Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y clang swig python3-dev
```

## Quick Start

### 1. Clone and Build
```bash
git clone <repository-url>
cd MolViewer/MolViewer
make
```

### 2. Start the Server
```bash
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
python3 server.py 8080
```

### 3. Access the Application
Open your web browser and navigate to:
```
http://localhost:8080
```

## Build Process

The build process involves several steps:

1. **Generate Python Bindings**: SWIG creates Python wrappers for C code
2. **Compile C Library**: Creates `libmol.so` shared library
3. **Build Python Module**: Creates `_molecule.so` Python extension

```bash
# Clean previous builds
make clean

# Build all components
make

# Verify build
ls -la *.so *.py
```

## Database Setup

The application automatically creates a SQLite database (`molecule.db`) with the following tables:

- **Elements**: Chemical element properties (atomic number, symbol, colors, radius)
- **Atoms**: Individual atom coordinates and element types
- **Bonds**: Connections between atoms
- **Molecules**: Molecular structure metadata
- **MoleculeAtom/MoleculeBond**: Relationship tables

### Initialize with Basic Elements:
```python
import molsql
db = molsql.Database(reset=False)
db.create_tables()
# Add common elements (H, C, N, O)
```

## Usage Guide

### Web Interface Tabs:

1. **Home**: Welcome page and project information
2. **Add/Remove Elements**: 
   - Add new chemical elements with custom properties
   - Remove existing elements from the database
3. **Upload SDF File**: 
   - Upload molecular structure files in SDF format
   - Specify molecule names for database storage
4. **Select From Molecules**: 
   - Browse uploaded molecules
   - View atom and bond counts
   - Select molecules for visualization
5. **Display Molecule**: 
   - Interactive 3D molecular visualization
   - Real-time rotation controls (X, Y, Z axes)
   - SVG-based rendering with element-specific colors

### API Endpoints:

- `GET /`: Main application interface
- `GET /getelements`: Retrieve all elements from database
- `GET /getsvg?moleculeName=<name>`: Get SVG representation of molecule
- `GET /getmolecules`: List all molecules with statistics
- `POST /uploadsuccess`: Upload new molecule from SDF file
- `POST /addelement`: Add new chemical element
- `POST /removeelement`: Remove element from database
- `POST /rotate`: Apply rotation transformation to molecule

## File Structure

```
MolViewer/
├── mol.c                 # Core C library implementation
├── mol.h                 # C library header file
├── molecule.i            # SWIG interface definition
├── MolDisplay.py         # Python visualization classes
├── molsql.py            # Database management
├── server.py            # Web server implementation
├── homepage.html        # Web interface
├── makefile             # Build configuration
├── README.md            # This file
└── __pycache__/         # Python bytecode cache
```

## Troubleshooting

### Common Issues:

1. **Import Error: "libmol.so: cannot open shared object file"**
   ```bash
   export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
   ```

2. **Port Already in Use**
   ```bash
   # Kill existing server
   ps aux | grep server.py
   kill <process_id>
   # Or use different port
   python3 server.py 8081
   ```

3. **Build Failures**
   ```bash
   # Clean and rebuild
   make clean
   make
   # Check for missing dependencies
   which clang swig python3
   ```

4. **Database Issues**
   ```bash
   # Reset database
   rm molecule.db
   # Restart server to recreate
   ```

## Testing

### Verify Installation:
```bash
# Test C library compilation
make libmol.so
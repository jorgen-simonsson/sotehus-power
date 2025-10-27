#!/usr/bin/env python3
"""
Launcher script for NiceGUI version
Run from project root: python run_nicegui.py
"""

import sys
import os

# Add project root to path so common modules can be imported
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set PYTHONPATH environment variable as well
os.environ['PYTHONPATH'] = project_root + os.pathsep + os.environ.get('PYTHONPATH', '')

if __name__ == "__main__":
    # Change to the frontend directory and run directly
    os.chdir(os.path.join(project_root, 'src', 'frontend'))
    
    # Now run the app by executing the file
    with open('nicegui_app.py') as f:
        code = compile(f.read(), 'nicegui_app.py', 'exec')
        exec(code)


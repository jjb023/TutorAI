#!/usr/bin/env python3
"""
Set up required directories for worksheet system
"""

import os

def setup_directories():
    """Create necessary directories for worksheet PDFs"""
    
    # Get the web directory path
    web_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create directories
    directories = [
        os.path.join(web_dir, 'static', 'worksheets'),
        os.path.join(web_dir, 'static', 'css'),
        os.path.join(web_dir, 'static', 'js'),
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")
    
    # Create a .gitignore in the worksheets directory to not commit PDFs
    gitignore_path = os.path.join(web_dir, 'static', 'worksheets', '.gitignore')
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write("# Ignore all PDFs\n*.pdf\n")
        print(f"✅ Created .gitignore in worksheets directory")

if __name__ == "__main__":
    setup_directories()

    
#!/usr/bin/env python3
"""
Build script for MediaPipe to Blender live animation add-on.
This script creates a ZIP file for distribution.
"""

import os
import sys
import shutil
import zipfile
import argparse
from datetime import datetime

def create_addon_zip(output_dir=None, version=None):
    """Create a ZIP file for the add-on."""
    print("Creating add-on ZIP file...")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set default output directory
    if output_dir is None:
        output_dir = os.path.join(script_dir, "dist")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set default version
    if version is None:
        version = "1.0.0"
    
    # Create temporary directory
    temp_dir = os.path.join(script_dir, "temp_build")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Create add-on directory
        addon_dir = os.path.join(temp_dir, "mediapipe_mocap")
        os.makedirs(addon_dir, exist_ok=True)
        
        # Copy Blender add-on files
        blender_addon_dir = os.path.join(script_dir, "blender", "4.0", "scripts", "addons", "mediapipe_mocap")
        if os.path.exists(blender_addon_dir):
            for item in os.listdir(blender_addon_dir):
                src = os.path.join(blender_addon_dir, item)
                dst = os.path.join(addon_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
        
        # Copy MediaPipe module
        mediapipe_module_dir = os.path.join(script_dir, "src", "mediapipe_module")
        if os.path.exists(mediapipe_module_dir):
            dst_module_dir = os.path.join(addon_dir, "mediapipe_module")
            os.makedirs(dst_module_dir, exist_ok=True)
            for item in os.listdir(mediapipe_module_dir):
                src = os.path.join(mediapipe_module_dir, item)
                dst = os.path.join(dst_module_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
        
        # Copy documentation
        docs_dir = os.path.join(script_dir, "docs")
        if os.path.exists(docs_dir):
            dst_docs_dir = os.path.join(addon_dir, "docs")
            os.makedirs(dst_docs_dir, exist_ok=True)
            for item in os.listdir(docs_dir):
                src = os.path.join(docs_dir, item)
                dst = os.path.join(dst_docs_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
        
        # Create ZIP file
        timestamp = datetime.now().strftime("%Y%m%d")
        zip_filename = f"mediapipe_mocap_v{version}_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(addon_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Add-on ZIP file created: {zip_path}")
        return zip_path
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build MediaPipe to Blender live animation add-on")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    parser.add_argument("--version", type=str, default="1.0.0", help="Add-on version")
    args = parser.parse_args()
    
    # Create add-on ZIP file
    zip_path = create_addon_zip(args.output, args.version)
    
    print(f"Build completed successfully: {zip_path}")

if __name__ == "__main__":
    main()

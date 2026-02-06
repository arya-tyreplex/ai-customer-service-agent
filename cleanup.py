"""
Cleanup Script - Remove Python cache and temporary files
"""

import os
import shutil
from pathlib import Path

def remove_pycache(root_dir="."):
    """Remove all __pycache__ directories."""
    removed = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip venv directory
        if 'venv' in dirpath or 'ENV' in dirpath:
            continue
        
        if '__pycache__' in dirnames:
            cache_path = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(cache_path)
                removed.append(cache_path)
                print(f"✅ Removed: {cache_path}")
            except Exception as e:
                print(f"❌ Failed to remove {cache_path}: {e}")
    
    return removed

def remove_pyc_files(root_dir="."):
    """Remove all .pyc files."""
    removed = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip venv directory
        if 'venv' in dirpath or 'ENV' in dirpath:
            continue
        
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    removed.append(file_path)
                    print(f"✅ Removed: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")
    
    return removed

def remove_temp_files(root_dir="."):
    """Remove temporary files."""
    removed = []
    temp_patterns = ['.tmp', '.temp', '~']
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip venv directory
        if 'venv' in dirpath or 'ENV' in dirpath:
            continue
        
        for filename in filenames:
            if any(filename.endswith(pattern) for pattern in temp_patterns):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    removed.append(file_path)
                    print(f"✅ Removed: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")
    
    return removed

def main():
    print("="*70)
    print("  TyrePlex Project Cleanup")
    print("="*70)
    
    print("\n1. Removing __pycache__ directories...")
    pycache_removed = remove_pycache()
    print(f"   Removed {len(pycache_removed)} __pycache__ directories")
    
    print("\n2. Removing .pyc files...")
    pyc_removed = remove_pyc_files()
    print(f"   Removed {len(pyc_removed)} .pyc files")
    
    print("\n3. Removing temporary files...")
    temp_removed = remove_temp_files()
    print(f"   Removed {len(temp_removed)} temporary files")
    
    total = len(pycache_removed) + len(pyc_removed) + len(temp_removed)
    
    print("\n" + "="*70)
    print(f"  Cleanup Complete! Removed {total} items")
    print("="*70)
    
    if total == 0:
        print("\n✨ Project is already clean!")
    else:
        print("\n✨ Project cleaned successfully!")

if __name__ == "__main__":
    main()

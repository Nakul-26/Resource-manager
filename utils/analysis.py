import os
import hashlib
from datetime import datetime
from collections import defaultdict

def scan_folder(folder_path):
    """
    Recursively scans a folder and returns a list of files with their metadata.
    """
    files_metadata = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                metadata = {
                    'name': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                }
                files_metadata.append(metadata)
            except OSError:
                # Ignore files that can't be accessed
                pass
    return files_metadata

def calculate_hash(file_path, block_size=65536):
    """
    Calculates the SHA256 hash of a file.
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def find_duplicates(files_metadata):
    """
    Finds duplicate files by first grouping by size, then hashing.
    """
    sizes = defaultdict(list)
    for file in files_metadata:
        sizes[file['size']].append(file)

    duplicates = defaultdict(list)
    for size, files in sizes.items():
        if len(files) > 1 and size > 0:
            hashes = defaultdict(list)
            for file in files:
                try:
                    file_hash = calculate_hash(file['path'])
                    hashes[file_hash].append(file['path'])
                except OSError:
                    pass
            
            for file_hash, paths in hashes.items():
                if len(paths) > 1:
                    duplicates[file_hash].extend(paths)
    
    # Return a dictionary of hash -> list of paths
    return dict(duplicates)
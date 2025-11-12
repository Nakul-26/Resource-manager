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
                    'hash': calculate_hash(file_path)
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
    Finds duplicate files based on their hash.
    """
    hashes = defaultdict(list)
    for file in files_metadata:
        hashes[file['hash']].append(file['path'])
    
    duplicates = {hash: paths for hash, paths in hashes.items() if len(paths) > 1}
    return duplicates
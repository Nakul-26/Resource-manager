import os
import zipfile
from PIL import Image

JUNK_EXTENSIONS = {
    '.DS_Store', '.log', '.bak', '.temp', '.tmp', '.cache', '.swp', '.pyc', '__pycache__'
}

def compress_files(file_paths, output_zip_path):
    """
    Compresses a list of files into a single zip file.
    """
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))
    return output_zip_path

def convert_images(file_paths, output_folder, format='WEBP'):
    """
    Converts images to a specified format (e.g., WEBP).
    """
    os.makedirs(output_folder, exist_ok=True)
    converted_files = []
    for file_path in file_paths:
        try:
            img = Image.open(file_path)
            new_filename = os.path.splitext(os.path.basename(file_path))[0] + f'.{format.lower()}'
            output_path = os.path.join(output_folder, new_filename)
            img.save(output_path, format=format)
            converted_files.append(output_path)
        except Exception as e:
            print(f"Could not convert {file_path}: {e}")
    return converted_files

def find_junk_files_and_empty_folders(folder_path):
    """
    Scans a directory to find junk files and empty folders.
    """
    junk_files = []
    empty_folders = []
    
    for root, dirs, files in os.walk(folder_path, topdown=False):
        is_empty = not files and not dirs
        
        # Check if the directory is empty or only contains junk
        if not dirs and all(os.path.splitext(f)[1] in JUNK_EXTENSIONS or f in JUNK_EXTENSIONS for f in files):
            empty_folders.append(root)

        for file in files:
            file_path = os.path.join(root, file)
            if os.path.splitext(file)[1] in JUNK_EXTENSIONS or file in JUNK_EXTENSIONS:
                junk_files.append(file_path)

        if is_empty and root != folder_path:
             if root not in empty_folders:
                empty_folders.append(root)

    return list(set(junk_files)), list(set(empty_folders))

import os
import zipfile
from PIL import Image

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

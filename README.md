# Resource Optimizer

A web-based tool to analyze and optimize files and folders for better storage, organization, and performance.

## Features

*   **File and Folder Analysis:** Scans uploaded files and folders to provide metadata and identify duplicates.
*   **Optimization Engine:**
    *   Compresses selected files into a ZIP archive.
    *   Converts images to the WebP format.
    *   Deletes duplicate files.
*   **Visualization:** Displays a pie chart of file types and a bar chart of folder sizes.

## Tech Stack

*   **Frontend:** HTML, CSS, JavaScript, Bootstrap, Chart.js
*   **Backend:** Python, Flask
*   **File Handling:** Python’s `os`, `shutil`, `hashlib`, `zipfile`, `Pillow`

## How to Run

1.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the Flask application:
    ```bash
    python3 app.py
    ```
3.  Open your browser and go to `http://127.0.0.1:5000`.
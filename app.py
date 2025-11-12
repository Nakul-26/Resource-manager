from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, make_response
import os
from utils.analysis import scan_folder, find_duplicates
from utils.optimization import compress_files, convert_images
from utils.recommendations import generate_recommendations
from collections import defaultdict

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
OPTIMIZED_FOLDER = 'static/optimized'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OPTIMIZED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OPTIMIZED_FOLDER'] = OPTIMIZED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

@app.template_filter('basename')
def basename(path):
    return os.path.basename(path)

@app.template_filter('get_file_size')
def get_file_size(path):
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return "N/A"

@app.errorhandler(413)
def too_large(e):
    return "File is too large. The limit is 100MB.", 413

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    files = request.files.getlist('file')
    
    # Clear the upload folder before each new upload
    for root, dirs, files_in_dir in os.walk(app.config['UPLOAD_FOLDER']):
        for f in files_in_dir:
            try:
                os.unlink(os.path.join(root, f))
            except OSError:
                pass # Ignore if file is already gone
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass # Ignore if dir is already gone

    for file in files:
        if file.filename == '':
            continue
        if file:
            path_parts = file.filename.split('/')
            relative_path = os.path.join(*path_parts) if len(path_parts) > 1 else file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    analysis_results = scan_folder(app.config['UPLOAD_FOLDER'])
    if not analysis_results:
        return "No files found to analyze. Please upload some files first."

    # Filtering logic
    filter_text = request.args.get('filter_text', '').lower()
    if filter_text:
        analysis_results = [
            file for file in analysis_results 
            if filter_text in file['name'].lower() or filter_text in file['path'].lower()
        ]

    # Sorting logic
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc') # 'asc' or 'desc'

    if sort_by in ['name', 'size', 'last_modified']:
        analysis_results.sort(key=lambda x: x[sort_by], reverse=(sort_order == 'desc'))

    duplicates = find_duplicates(analysis_results)
    recommendations = generate_recommendations(analysis_results, duplicates)

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 25
    total_files = len(analysis_results)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_files = analysis_results[start:end]
    total_pages = (total_files + PER_PAGE - 1) // PER_PAGE

    # Get largest files
    largest_files = sorted(analysis_results, key=lambda x: x['size'], reverse=True)[:5]

    # Get recently modified files (most recently modified)
    recently_modified_files = sorted(analysis_results, key=lambda x: x['last_modified'], reverse=True)[:5]

    # Prepare data for charts
    file_types = defaultdict(int)
    folder_sizes = defaultdict(int)
    for file_meta in analysis_results:
        ext = os.path.splitext(file_meta['name'])[1] or 'No Extension'
        file_types[ext] += 1
        relative_path = os.path.relpath(os.path.dirname(file_meta['path']), app.config['UPLOAD_FOLDER'])
        folder_name = relative_path.split('/')[0] if relative_path != '.' else 'Root'
        folder_sizes[folder_name] += file_meta['size']

    return render_template('dashboard.html', 
                           files=paginated_files,
                           duplicates=duplicates,
                           recommendations=recommendations,
                           file_types=list(file_types.keys()),
                           file_type_counts=list(file_types.values()),
                           folder_names=list(folder_sizes.keys()),
                           folder_sizes=list(folder_sizes.values()),
                           page=page,
                           total_pages=total_pages,
                           largest_files=largest_files,
                           recently_modified_files=recently_modified_files,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           filter_text=filter_text)

@app.route('/optimize', methods=['POST'])
def optimize():
    selected_files = request.form.getlist('selected_files')
    optimization_type = request.form.get('optimization_type')

    if not selected_files:
        return "No files selected for optimization."

    if optimization_type == 'compress':
        zip_path = os.path.join(app.config['OPTIMIZED_FOLDER'], 'optimized.zip')
        compress_files(selected_files, zip_path)
        return send_file(zip_path, as_attachment=True)
    elif optimization_type == 'convert_images':
        converted_files = convert_images(selected_files, app.config['OPTIMIZED_FOLDER'])
        return f"Converted {len(converted_files)} images."
    elif optimization_type == 'delete_duplicates':
        for file_path in selected_files:
            os.remove(file_path)
        return redirect(url_for('dashboard'))
    
    return "Invalid optimization type."

@app.route('/report/csv')
def generate_csv_report():
    analysis_results = scan_folder(app.config['UPLOAD_FOLDER'])
    if not analysis_results:
        return "No data to generate report.", 404

    # Create CSV content
    csv_data = "Name,Path,Size (bytes),Last Modified,Hash\n"
    for file_meta in analysis_results:
        csv_data += f'"{file_meta["name"]}","{file_meta["path"]}",{file_meta["size"]},"{file_meta["last_modified"]}","{file_meta["hash"]}"\n'

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=resource_report.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(debug=True)

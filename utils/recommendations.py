import os
from collections import defaultdict

# Heuristic for estimated savings. In a real app, this could be more sophisticated.
WEBP_CONVERSION_SAVINGS_RATIO = 0.30  # Assume 30% savings
COMMON_TEMP_EXTENSIONS = ['.tmp', '.log', '.bak', '.swp']

def generate_recommendations(analysis_results, duplicates):
    """
    Analyzes file data and generates a list of optimization recommendations.
    """
    recommendations = []

    # Rule 1: Suggest image conversion
    image_conversion_candidates = []
    total_image_size = 0
    for file in analysis_results:
        if file['name'].lower().endswith(('.png', '.jpg', '.jpeg')):
            image_conversion_candidates.append(file)
            total_image_size += file['size']
    
    if image_conversion_candidates:
        estimated_savings = total_image_size * WEBP_CONVERSION_SAVINGS_RATIO
        if estimated_savings > 1024 * 1024: # Only recommend if savings are > 1MB
            recommendations.append({
                'text': f"You could save ~{estimated_savings / (1024*1024):.2f} MB by converting {len(image_conversion_candidates)} images to WebP.",
                'type': 'CONVERT_IMAGES',
                'estimated_savings_bytes': estimated_savings
            })

    # Rule 2: Suggest duplicate deletion
    if duplicates:
        total_duplicate_size = 0
        num_duplicate_files = 0
        for hash, paths in duplicates.items():
            original_size = os.path.getsize(paths[0])
            total_duplicate_size += original_size * (len(paths) - 1)
            num_duplicate_files += (len(paths) - 1)

        if total_duplicate_size > 0:
            recommendations.append({
                'text': f"You can free up {total_duplicate_size / (1024*1024):.2f} MB by deleting {num_duplicate_files} duplicate files.",
                'type': 'DELETE_DUPLICATES',
                'estimated_savings_bytes': total_duplicate_size
            })

    # Rule 3: Suggest temporary file cleanup
    temp_files = []
    total_temp_size = 0
    for file in analysis_results:
        if any(file['name'].lower().endswith(ext) for ext in COMMON_TEMP_EXTENSIONS):
            temp_files.append(file)
            total_temp_size += file['size']

    if total_temp_size > 1024: # Only recommend if savings are > 1KB
        recommendations.append({
            'text': f"You can clear {total_temp_size / 1024:.2f} KB by removing {len(temp_files)} temporary files.",
            'type': 'DELETE_TEMP_FILES',
            'estimated_savings_bytes': total_temp_size
        })
        
    # Sort recommendations by potential savings
    recommendations.sort(key=lambda x: x.get('estimated_savings_bytes', 0), reverse=True)

    return recommendations

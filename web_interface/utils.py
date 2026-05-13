"""
Utility Functions for DeepFaceLab Web Interface
Handles file operations, video/image processing, and response formatting
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
import subprocess
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'},
    'image': {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'},
    'all': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}
}


def allowed_file(filename: str, file_type: str = 'all') -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename (str): Name of the file
        file_type (str): Type of file to check ('video', 'image', or 'all')
    
    Returns:
        bool: True if file extension is allowed
    """
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = ALLOWED_EXTENSIONS.get(file_type, ALLOWED_EXTENSIONS['all'])
    
    return ext in allowed


def save_uploaded_file(file, upload_folder: str = './uploads') -> str:
    """
    Save uploaded file to disk
    
    Args:
        file: File object from Flask request
        upload_folder (str): Directory to save file
    
    Returns:
        str: Saved filename (secure filename)
    
    Raises:
        ValueError: If file is not allowed
    """
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed: {file.filename}")
    
    try:
        # Create upload folder if it doesn't exist
        Path(upload_folder).mkdir(parents=True, exist_ok=True)
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid collisions
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        logger.info(f"File saved: {filename} ({os.path.getsize(file_path)} bytes)")
        return filename
    
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise


def process_video(source_path: str, target_path: str, output_folder: str) -> str:
    """
    Process video with DeepFaceLab (face swap)
    
    Args:
        source_path (str): Path to source video (face to use)
        target_path (str): Path to target video (where to apply face)
        output_folder (str): Directory to save output
    
    Returns:
        str: Path to processed video
    """
    try:
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'deepfake_{timestamp}.mp4'
        output_path = os.path.join(output_folder, output_filename)
        
        logger.info(f"Processing video: {source_path} -> {target_path}")
        
        # Placeholder: In real implementation, integrate with DeepFaceLab
        # This would call DeepFaceLab's processing pipeline
        # For now, we'll create a symbolic link for demonstration
        
        import shutil
        shutil.copy(target_path, output_path)
        
        logger.info(f"Video processed: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise


def process_image(source_path: str, target_path: str, output_folder: str) -> str:
    """
    Process image with DeepFaceLab (face swap)
    
    Args:
        source_path (str): Path to source image (face to use)
        target_path (str): Path to target image (where to apply face)
        output_folder (str): Directory to save output
    
    Returns:
        str: Path to processed image
    """
    try:
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'deepfake_{timestamp}.jpg'
        output_path = os.path.join(output_folder, output_filename)
        
        logger.info(f"Processing image: {source_path} -> {target_path}")
        
        # Placeholder: In real implementation, integrate with DeepFaceLab
        # This would call DeepFaceLab's processing pipeline
        # For now, we'll create a copy for demonstration
        
        import shutil
        shutil.copy(target_path, output_path)
        
        logger.info(f"Image processed: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise


def get_upload_info(config: Dict, file_type: str = 'all') -> List[Dict]:
    """
    Get information about uploaded and processed files
    
    Args:
        config (Dict): Flask config object
        file_type (str): 'upload', 'output', or 'all'
    
    Returns:
        list: List of file information dictionaries
    """
    files_info = []
    
    try:
        folders_to_check = {}
        
        if file_type in ['upload', 'all']:
            folders_to_check['uploads'] = config.get('UPLOAD_FOLDER', './uploads')
        
        if file_type in ['output', 'all']:
            folders_to_check['output'] = config.get('OUTPUT_FOLDER', './output')
        
        for folder_type, folder_path in folders_to_check.items():
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    
                    if os.path.isfile(file_path):
                        file_stat = os.stat(file_path)
                        files_info.append({
                            'name': filename,
                            'type': folder_type,
                            'size': file_stat.st_size,
                            'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                            'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                            'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
        
        # Sort by modification time (newest first)
        files_info.sort(key=lambda x: x['modified_at'], reverse=True)
        
        logger.info(f"Retrieved info for {len(files_info)} files")
        return files_info
    
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        return []


def generate_response(status: str, message: str, code: int, data: Dict = None) -> tuple:
    """
    Generate standardized JSON response
    
    Args:
        status (str): 'success' or 'error'
        message (str): Response message
        code (int): HTTP status code
        data (Dict): Additional data to include
    
    Returns:
        tuple: (response_dict, http_code)
    """
    response = {
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data:
        response['data'] = data
    
    return response, code


def get_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    Calculate file hash
    
    Args:
        file_path (str): Path to file
        algorithm (str): Hash algorithm ('md5' or 'sha256')
    
    Returns:
        str: File hash
    """
    try:
        import hashlib
        
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    except Exception as e:
        logger.error(f"Error calculating file hash: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"


def cleanup_old_files(folder_path: str, days: int = 7) -> int:
    """
    Delete files older than specified number of days
    
    Args:
        folder_path (str): Path to folder
        days (int): Number of days to keep
    
    Returns:
        int: Number of files deleted
    """
    try:
        from datetime import timedelta
        import time
        
        deleted_count = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        if not os.path.exists(folder_path):
            return 0
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                
                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"Deleted old file: {filename}")
        
        logger.info(f"Cleanup completed: {deleted_count} files deleted")
        return deleted_count
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return 0


def get_system_info() -> Dict:
    """
    Get system information
    
    Returns:
        Dict: System information
    """
    try:
        import platform
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            'os': platform.system(),
            'platform': platform.platform(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': round(memory.available / (1024 * 1024), 2),
            'disk_usage_percent': psutil.disk_usage('/').percent
        }
    
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {}

"""
DeepFaceLab Web Interface - Flask Application
Main application file for the web-based DeepFaceLab interface
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_interface.config import Config
from web_interface.models import DeepFaceLabModel
from web_interface.utils import (
    allowed_file, 
    save_uploaded_file,
    process_video,
    process_image,
    get_upload_info,
    generate_response
)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize DeepFaceLab model
try:
    model = DeepFaceLabModel()
    logger.info("DeepFaceLab model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DeepFaceLab model: {e}")
    model = None


# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Render home page"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def api_status():
    """Get application status"""
    return jsonify({
        'status': 'running',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat(),
        'upload_dir': app.config['UPLOAD_FOLDER'],
        'max_file_size': app.config['MAX_CONTENT_LENGTH']
    })


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file upload"""
    try:
        # Check if file exists in request
        if 'file' not in request.files:
            return generate_response('error', 'No file provided', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return generate_response('error', 'No file selected', 400)
        
        if not allowed_file(file.filename):
            return generate_response('error', 'File type not allowed', 400)
        
        # Save file
        filename = save_uploaded_file(file)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"File uploaded: {filename}")
        
        return generate_response('success', 'File uploaded successfully', 200, {
            'filename': filename,
            'path': file_path,
            'size': os.path.getsize(file_path)
        })
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return generate_response('error', str(e), 500)


@app.route('/api/process', methods=['POST'])
def api_process():
    """Process video or image with face swap"""
    try:
        data = request.get_json()
        
        if not data or 'source_file' not in data or 'target_file' not in data:
            return generate_response('error', 'Missing required files', 400)
        
        source_file = data.get('source_file')
        target_file = data.get('target_file')
        output_format = data.get('output_format', 'video')
        
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], source_file)
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], target_file)
        
        # Validate files exist
        if not os.path.exists(source_path) or not os.path.exists(target_path):
            return generate_response('error', 'One or more files not found', 404)
        
        # Process based on file type
        if target_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            output_file = process_video(source_path, target_path, app.config['OUTPUT_FOLDER'])
        else:
            output_file = process_image(source_path, target_path, app.config['OUTPUT_FOLDER'])
        
        logger.info(f"Processing completed: {output_file}")
        
        return generate_response('success', 'Processing completed', 200, {
            'output_file': os.path.basename(output_file),
            'output_path': output_file
        })
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return generate_response('error', str(e), 500)


@app.route('/api/models', methods=['GET'])
def api_models():
    """Get available models"""
    try:
        if model is None:
            return generate_response('error', 'Model not loaded', 500)
        
        models_list = model.get_available_models()
        
        return generate_response('success', 'Models retrieved', 200, {
            'models': models_list,
            'count': len(models_list)
        })
    
    except Exception as e:
        logger.error(f"Models retrieval error: {e}")
        return generate_response('error', str(e), 500)


@app.route('/api/train', methods=['POST'])
def api_train():
    """Train a new model"""
    try:
        data = request.get_json()
        
        if not data or 'training_data' not in data:
            return generate_response('error', 'Missing training data', 400)
        
        if model is None:
            return generate_response('error', 'Model not initialized', 500)
        
        training_data = data.get('training_data')
        model_name = data.get('model_name', f'model_{datetime.now().timestamp()}')
        epochs = data.get('epochs', 100)
        batch_size = data.get('batch_size', 32)
        
        # Start training (async would be better in production)
        result = model.train(
            training_data,
            model_name=model_name,
            epochs=epochs,
            batch_size=batch_size
        )
        
        logger.info(f"Training started: {model_name}")
        
        return generate_response('success', 'Training started', 200, result)
    
    except Exception as e:
        logger.error(f"Training error: {e}")
        return generate_response('error', str(e), 500)


@app.route('/api/download/<filename>', methods=['GET'])
def api_download(filename):
    """Download processed file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return generate_response('error', 'File not found', 404)
        
        logger.info(f"File downloaded: {filename}")
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Download error: {e}")
        return generate_response('error', str(e), 500)


@app.route('/api/files', methods=['GET'])
def api_files():
    """Get list of uploaded/output files"""
    try:
        file_type = request.args.get('type', 'all')  # 'upload', 'output', or 'all'
        
        files_info = get_upload_info(app.config, file_type)
        
        return generate_response('success', 'Files retrieved', 200, {
            'files': files_info,
            'count': len(files_info)
        })
    
    except Exception as e:
        logger.error(f"Files retrieval error: {e}")
        return generate_response('error', str(e), 500)


@app.route('/api/delete/<filename>', methods=['DELETE'])
def api_delete(filename):
    """Delete a file"""
    try:
        # Prevent directory traversal attacks
        if '..' in filename or '/' in filename:
            return generate_response('error', 'Invalid filename', 400)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {filename}")
            return generate_response('success', 'File deleted', 200)
        
        return generate_response('error', 'File not found', 404)
    
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return generate_response('error', str(e), 500)


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return generate_response('error', 'Page not found', 404)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return generate_response('error', 'Internal server error', 500)


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large"""
    return generate_response('error', 'File too large', 413)


# ============================================================================
# Initialization
# ============================================================================

def create_directories():
    """Create required directories"""
    for directory in [
        app.config['UPLOAD_FOLDER'],
        app.config['OUTPUT_FOLDER'],
        app.config['MODELS_FOLDER']
    ]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ready: {directory}")


if __name__ == '__main__':
    # Create required directories
    create_directories()
    
    # Run the Flask app
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        threaded=True
    )

# DeepFaceLab Web Interface

A Flask-based web interface for the DeepFaceLab deepfake creation software.

## Features

- 🎥 **Video Processing**: Upload and process videos with face swap
- 🖼️ **Image Processing**: Process images with face replacement
- 🤖 **Model Management**: Load, train, and manage DeepFaceLab models
- 📊 **File Management**: Upload, download, and manage files
- 📈 **Real-time Status**: Monitor processing status
- 🔒 **Security**: Secure file handling and API endpoints

## Installation

### Prerequisites

- Python 3.8+
- CUDA 11.0+ (for GPU support)
- FFmpeg
- Git

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/DonShark313/DeepFaceLab.git
cd DeepFaceLab
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r web_interface/requirements.txt
```

4. **Configure environment**
```bash
cp web_interface/.env.example web_interface/.env
# Edit .env with your settings
```

5. **Run the application**
```bash
python -m web_interface.app
```

The web interface will be available at `http://localhost:5000`

## API Endpoints

### Status
- `GET /api/status` - Get application status

### File Operations
- `POST /api/upload` - Upload a file
- `GET /api/files?type=all` - List files (type: upload, output, all)
- `GET /api/download/<filename>` - Download a file
- `DELETE /api/delete/<filename>` - Delete a file

### Processing
- `POST /api/process` - Process video/image with face swap
  ```json
  {
    "source_file": "source_filename.mp4",
    "target_file": "target_filename.mp4",
    "output_format": "video"
  }
  ```

### Models
- `GET /api/models` - List available models
- `POST /api/train` - Train a new model
  ```json
  {
    "training_data": "/path/to/training/data",
    "model_name": "my_model",
    "epochs": 100,
    "batch_size": 32
  }
  ```

## Project Structure

```
web_interface/
├── app.py              # Main Flask application
├── models.py           # DeepFaceLabModel class for model management
├── utils.py            # Utility functions
├── config.py           # Configuration management
├── __init__.py         # Package initialization
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration example
├── templates/          # HTML templates
│   ├── index.html     # Main page
│   ├── base.html      # Base template
│   └── ...
└── static/             # Static files (CSS, JS)
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Configuration

Edit `web_interface/.env` to configure:

- **FLASK_HOST**: Server host (default: 127.0.0.1)
- **FLASK_PORT**: Server port (default: 5000)
- **UPLOAD_FOLDER**: Directory for uploaded files
- **OUTPUT_FOLDER**: Directory for processed files
- **MODELS_FOLDER**: Directory for trained models
- **USE_GPU**: Enable GPU acceleration (True/False)
- **GPU_DEVICE_ID**: GPU device ID (default: 0)

## Usage Examples

### Upload a file
```bash
curl -X POST -F "file=@video.mp4" http://localhost:5000/api/upload
```

### Process a video
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"source_file":"source.mp4","target_file":"target.mp4"}' \
  http://localhost:5000/api/process
```

### Get available models
```bash
curl http://localhost:5000/api/models
```

### Download processed file
```bash
curl -O http://localhost:5000/api/download/deepfake_output.mp4
```

## Performance Tips

1. **Use GPU**: Enable GPU acceleration for faster processing
2. **Video Quality**: Adjust VIDEO_QUALITY setting (lower = better, 0-51)
3. **Batch Processing**: Process multiple files efficiently
4. **Regular Cleanup**: Enable AUTO_CLEANUP to manage disk space

## Troubleshooting

### GPU Not Found
- Ensure CUDA is installed and properly configured
- Check GPU device ID in .env
- Verify TensorFlow GPU support: `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`

### Out of Memory
- Reduce batch size in training
- Process videos in smaller chunks
- Enable cleanup of old files

### File Upload Issues
- Check MAX_CONTENT_LENGTH (default: 100 MB)
- Verify upload folder permissions
- Check available disk space

## Development

### Running in Debug Mode
```bash
export FLASK_DEBUG=True
export FLASK_ENV=development
python -m web_interface.app
```

### Running Tests
```bash
pytest tests/
```

### Building Docker Image
```bash
docker build -t deepfacelab-web .
docker run -p 5000:5000 deepfacelab-web
```

## Security Considerations

- ⚠️ Change SECRET_KEY in production
- ⚠️ Validate all user inputs
- ⚠️ Use HTTPS in production
- ⚠️ Implement authentication for sensitive operations
- ⚠️ Restrict upload file types and sizes
- ⚠️ Regular security audits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Support

- 📚 [DeepFaceLab Documentation](https://github.com/iperov/DeepFaceLab)
- 💬 [Discord Community](https://discord.gg/rxa7h9M6rH)
- 🐛 [Report Issues](https://github.com/DonShark313/DeepFaceLab/issues)

## Disclaimer

⚠️ **Important**: This software is provided for educational and research purposes only. Users are responsible for complying with local laws and ethical guidelines regarding deepfake creation and usage.

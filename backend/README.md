# ASCIICam Backend

A Python FastAPI backend for a Raspberry Pi-based offline camera system that captures photos and converts ### 2. Convert to Halftone

```bash
curl -X POST "http://localhost:5000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "halftone",
    "dot_size": 8,
    "dot_resolution": 5,
    "screen_angle": 45.0,
    "invert": false
  }'
```

**Enhanced Halftone Parameters:**
- `dot_size`: Maximum dot radius (1-20, default: 8)
- `dot_resolution`: Distance between dot centers (2-15, default: 5)  
- `screen_angle`: Screen rotation angle in degrees (0-360, default: 0.0)
- `invert`: Invert halftone pattern (default: false)
- `threshold`: Grayscale threshold - for compatibility (default: 127)

**Legacy Parameters (still supported):**
- `dot_spacing`: Use `dot_resolution` instead
- `angle`: Use `screen_angle` insteadone or ASCII art for printing.

## Features

- **Camera Support**: Prioritizes Raspberry Pi camera with USB webcam fallback
- **Configurable Resolution**: Set capture resolution via API parameters
- **Halftone Processing**: Grayscale halftone with configurable dot patterns, spacing, and rotation
- **ASCII Art**: Convert images to ASCII art and render as high-quality images
- **History Management**: Maintains history of all processed images
- **Print Integration**: CUPS-based printing for both images and ASCII text
- **Error Handling**: Comprehensive error responses with retry mechanisms

## API Endpoints

### Core Functionality

- `POST /capture` - Capture photo using camera
- `POST /convert` - Convert photo to halftone or ASCII
- `GET /preview` - Get processed image preview
- `POST /print` - Print processed image or ASCII text

### System Management

- `GET /status` - System status (camera, printer, files)
- `GET /printers` - Available printers
- `GET /history` - Processing history
- `DELETE /history` - Clear history

## Installation

### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y cups cups-client
sudo apt install -y fonts-dejavu-core

# For Raspberry Pi camera support
sudo apt install -y python3-picamera2

# Enable camera (Raspberry Pi)
sudo raspi-config  # Enable camera interface
```

### Setup

1. **Clone and setup the project:**
```bash
cd /home/rishi/devmt/asciicam/backend
chmod +x run.sh
```

2. **Configure settings (optional):**
```bash
# Edit .env file to customize settings
nano .env
```

3. **Run the server:**
```bash
./run.sh
```

The server will start on `http://0.0.0.0:5000`

## Configuration

### Environment Variables (.env)

```env
# Camera Settings
DEFAULT_RESOLUTION_WIDTH=1280
DEFAULT_RESOLUTION_HEIGHT=720
CAMERA_RETRY_ATTEMPTS=3

# Image Processing
DEFAULT_DOT_SPACING=5
DEFAULT_THRESHOLD=127
ASCII_FONT_SIZE=8
ASCII_DPI=300

# Storage
MAX_HISTORY_FILES=100

# Server
HOST=0.0.0.0
PORT=5000
DEBUG=true
```

## API Usage Examples

### 1. Capture Photo

```bash
curl -X POST "http://localhost:5000/capture" \
  -H "Content-Type: application/json" \
  -d '{
    "width": 1920,
    "height": 1080,
    "camera_preference": "auto"
  }'
```

**Response:**
```json
{
  "success": true,
  "camera_type": "pi_camera",
  "timestamp": "2024-01-15T10:30:00",
  "file_path": "./static/photo.jpg",
  "resolution": [1920, 1080],
  "message": "Photo captured successfully",
  "history": {
    "history_path": "./static/history/captures/capture_20240115_103000.jpg"
  }
}
```

### 2. Convert to Halftone

```bash
curl -X POST "http://localhost:5000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "halftone",
    "dot_spacing": 8,
    "threshold": 127,
    "invert": false,
    "angle": 45.0
  }'
```

### 3. Convert to ASCII

```bash
curl -X POST "http://localhost:5000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ascii",
    "char_width": 100,
    "invert": false,
    "font_size": 10
  }'
```

### 4. Print Image

```bash
curl -X POST "http://localhost:5000/print" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_name": "HP_LaserJet",
    "copies": 1,
    "paper_size": "A4",
    "print_text": false
  }'
```

### 5. Get System Status

```bash
curl "http://localhost:5000/status"
```

## Project Structure

```
backend/
├── app.py              # FastAPI main application
├── camera.py           # Camera management (Pi Camera + USB)
├── halftone.py         # Halftone and ASCII processing
├── printer.py          # CUPS printing integration
├── history.py          # History management
├── requirements.txt    # Python dependencies
├── .env               # Configuration file
├── run.sh             # Startup script
└── static/            # Static files and history
    ├── photo.jpg      # Current captured photo
    ├── preview.png    # Current processed image
    └── history/       # Historical files
        ├── captures/  # Original photos
        └── processed/ # Processed images
```

## Camera Configuration

The system supports configurable camera preferences:

- `"auto"` - Try Pi camera first, fallback to USB
- `"pi"` - Use only Raspberry Pi camera
- `"usb"` - Use only USB webcam

## Halftone Algorithm

Based on the JavaScript reference provided, implements:
- **Granular Control**: Separate dot size and spacing parameters
- **Screen Angles**: Configurable rotation angles for varied effects
- **Grayscale Conversion**: Uses luminance formula (0.299*R + 0.587*G + 0.114*B)
- **Anti-aliased Rendering**: Smooth output with high-quality circle drawing

### Halftone Parameters

- **`dot_size`**: Controls the maximum radius of halftone dots (1-20)
  - Smaller values = finer detail, less ink coverage
  - Larger values = bolder effect, more ink coverage

- **`dot_resolution`**: Controls spacing between dot centers (2-15)  
  - Smaller values = tighter dot pattern, higher resolution
  - Larger values = looser pattern, faster processing

- **`screen_angle`**: Rotation angle of the halftone screen (0-360°)
  - 0° = horizontal/vertical alignment
  - 45° = traditional newspaper halftone angle
  - Custom angles for artistic effects

- **`invert`**: Reverses the halftone pattern
  - false = dark areas get large dots (normal)
  - true = bright areas get large dots (inverted)

## ASCII Art Features

- Configurable character width and font size
- High-quality image rendering using system fonts
- Text file output alongside image output
- Maintains aspect ratio in conversion

## Error Handling

- Comprehensive error responses with detailed messages
- Camera retry mechanisms on failure
- Graceful fallback between camera types
- Print job status monitoring

## Troubleshooting

### Camera Issues

```bash
# Check camera detection
v4l2-ctl --list-devices

# Test Pi camera (if available)
libcamera-hello --timeout 2000

# Check permissions
sudo usermod -a -G video $USER
```

**Note**: The "Failed to initialize Pi Camera: No module named 'picamera2'" warning is normal on non-Raspberry Pi systems. The system will automatically fall back to USB camera.

### Printing Issues

```bash
# Check CUPS status
systemctl status cups

# List available printers
lpstat -p

# Test print
echo "test" | lp
```

### API Issues

If you get 400 Bad Request errors:
- Ensure all required parameters are provided
- Check that photo.jpg exists before calling /convert
- Verify JSON format in POST requests

### Dependencies

```bash
# Reinstall OpenCV if issues
pip uninstall opencv-python
pip install opencv-python==4.8.1.78

# Check Pillow version
pip install --upgrade Pillow
```

## Development

To run in development mode:

```bash
# Install development dependencies
pip install fastapi[all] uvicorn[standard]

# Run with auto-reload
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### Testing

Test the conversion system:

```bash
# Test basic image processing functions
python3 test_conversion.py

# Test enhanced halftone parameters
python3 test_halftone_params.py

# Test API endpoints (with server running)
./test_api.sh
```

## License

This project is designed for educational and personal use with Raspberry Pi camera systems.

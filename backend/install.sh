#!/bin/bash

# ASCIICam System Dependencies Installer

echo "Installing ASCIICam system dependencies..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install basic development tools
echo "🔧 Installing development tools..."
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install OpenCV system dependencies
echo "👁️ Installing OpenCV dependencies..."
sudo apt install -y libopencv-dev python3-opencv libgl1-mesa-glx libglib2.0-0

# Install image processing libraries
echo "🖼️ Installing image processing libraries..."
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev libwebp-dev

# Install font libraries
echo "📝 Installing font libraries..."
sudo apt install -y fonts-dejavu-core fonts-liberation ttf-mscorefonts-installer

# Install CUPS for printing (optional)
echo "🖨️ Installing CUPS printing system..."
sudo apt install -y cups cups-client

# Install camera dependencies (Raspberry Pi specific)
if [[ $(uname -m) == "arm"* ]] || [[ $(uname -m) == "aarch64" ]]; then
    echo "🎥 Installing Raspberry Pi camera dependencies..."
    sudo apt install -y python3-picamera2 libcamera-dev libcamera-tools
    
    # Enable camera if on Raspberry Pi
    echo "📹 To enable the camera, run: sudo raspi-config"
    echo "   Navigate to Interface Options > Camera > Enable"
fi

# Install v4l-utils for USB camera debugging
echo "📷 Installing USB camera utilities..."
sudo apt install -y v4l-utils

echo ""
echo "✅ System dependencies installation complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Run ./run.sh to start the server"
echo "   2. Visit http://localhost:5000/docs for API documentation"
echo "   3. Use ./test.sh to verify the installation"
echo ""
echo "💡 For Raspberry Pi users:"
echo "   - Enable camera: sudo raspi-config"
echo "   - Test Pi camera: libcamera-hello --timeout 2000"
echo "   - Test USB camera: v4l2-ctl --list-devices"

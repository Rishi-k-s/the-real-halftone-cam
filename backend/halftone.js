class HalftoneConverter {
    constructor() {
        this.sourceCanvas = document.getElementById('sourceCanvas');
        this.targetCanvas = document.getElementById('targetCanvas');
        this.sourceCtx = this.sourceCanvas.getContext('2d');
        this.targetCtx = this.targetCanvas.getContext('2d');
        this.currentImage = null;
        
        // Enable anti-aliasing and smooth rendering
        this.sourceCtx.imageSmoothingEnabled = true;
        this.sourceCtx.imageSmoothingQuality = 'high';
        this.targetCtx.imageSmoothingEnabled = true;
        this.targetCtx.imageSmoothingQuality = 'high';
        
        this.initializeEventListeners();
        this.initializeControls();
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const imageInput = document.getElementById('imageInput');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const printBtn = document.getElementById('printBtn');
        const resetBtn = document.getElementById('resetBtn');

        // File upload handling
        uploadArea.addEventListener('click', () => imageInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        imageInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Button handlers
        generateBtn.addEventListener('click', this.generateHalftone.bind(this));
        downloadBtn.addEventListener('click', this.downloadResult.bind(this));
        printBtn.addEventListener('click', this.printResult.bind(this));
        resetBtn.addEventListener('click', this.reset.bind(this));

        // Real-time control updates
        const controls = ['dotSize', 'dotResolution', 'angle', 'halftoneColor', 'backgroundColor', 'effectType'];
        controls.forEach(id => {
            const element = document.getElementById(id);
            element.addEventListener('input', this.updateControlValues.bind(this));
        });
    }

    initializeControls() {
        this.updateControlValues();
    }

    updateControlValues() {
        const dotSize = document.getElementById('dotSize');
        const dotResolution = document.getElementById('dotResolution');
        const angle = document.getElementById('angle');

        document.getElementById('dotSizeValue').textContent = dotSize.value;
        document.getElementById('dotResolutionValue').textContent = dotResolution.value;
        document.getElementById('angleValue').textContent = angle.value;
    }

    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.loadImage(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.loadImage(file);
        }
    }

    loadImage(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                this.currentImage = img;
                this.displayOriginalImage();
                document.getElementById('controlsSection').style.display = 'block';
                document.getElementById('controlsSection').classList.add('fade-in');
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    displayOriginalImage() {
        const maxWidth = 400;
        const maxHeight = 400;
        
        let { width, height } = this.currentImage;
        
        // Calculate aspect ratio and resize if needed
        if (width > maxWidth || height > maxHeight) {
            const aspectRatio = width / height;
            if (width > height) {
                width = maxWidth;
                height = maxWidth / aspectRatio;
            } else {
                height = maxHeight;
                width = maxHeight * aspectRatio;
            }
        }

        this.sourceCanvas.width = width;
        this.sourceCanvas.height = height;
        
        // Enable high-quality image rendering
        this.sourceCtx.imageSmoothingEnabled = true;
        this.sourceCtx.imageSmoothingQuality = 'high';
        
        this.sourceCtx.drawImage(this.currentImage, 0, 0, width, height);
    }

    async startCamera() {
        try {
            // Request camera access with preferred constraints
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera on mobile devices
                }
            };

            this.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            const video = document.getElementById('cameraVideo');
            const cameraContainer = document.getElementById('cameraContainer');
            
            video.srcObject = this.cameraStream;
            cameraContainer.style.display = 'block';
            cameraContainer.classList.add('fade-in');
            
            // Update button text
            document.getElementById('cameraBtn').textContent = 'Camera Active';
            document.getElementById('cameraBtn').style.opacity = '0.7';
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            let errorMessage = 'Unable to access camera. ';
            
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Please allow camera permissions and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'No camera found on this device.';
            } else if (error.name === 'NotSupportedError') {
                errorMessage += 'Camera not supported in this browser.';
            } else {
                errorMessage += 'Please check your camera connection and try again.';
            }
            
            alert(errorMessage);
        }
    }

    capturePhoto() {
        const video = document.getElementById('cameraVideo');
        
        if (!video.videoWidth || !video.videoHeight) {
            alert('Camera not ready. Please wait a moment and try again.');
            return;
        }

        // Create a canvas to capture the photo
        const captureCanvas = document.createElement('canvas');
        const captureCtx = captureCanvas.getContext('2d');
        
        // Set canvas size to video dimensions
        captureCanvas.width = video.videoWidth;
        captureCanvas.height = video.videoHeight;
        
        // Draw the current video frame to canvas
        captureCtx.drawImage(video, 0, 0);
        
        // Convert canvas to image
        captureCanvas.toBlob((blob) => {
            const img = new Image();
            img.onload = () => {
                this.currentImage = img;
                this.displayOriginalImage();
                this.stopCamera();
                
                // Show controls section
                document.getElementById('controlsSection').style.display = 'block';
                document.getElementById('controlsSection').classList.add('fade-in');
            };
            img.src = URL.createObjectURL(blob);
        }, 'image/jpeg', 0.95);
    }

    stopCamera() {
        if (this.cameraStream) {
            // Stop all tracks
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
            
            // Clear video source
            const video = document.getElementById('cameraVideo');
            video.srcObject = null;
            
            // Hide camera container
            const cameraContainer = document.getElementById('cameraContainer');
            cameraContainer.style.display = 'none';
            
            // Reset camera button
            const cameraBtn = document.getElementById('cameraBtn');
            cameraBtn.innerHTML = '<span class="camera-icon">📷</span>Take Photo';
            cameraBtn.style.opacity = '1';
        }
    }

    // Utility functions from the reference
    positionToDataIndex(x, y, width) {
        return (y * width + x) * 4;
    }

    map(value, minA, maxA, minB, maxB) {
        return ((value - minA) / (maxA - minA)) * (maxB - minB) + minB;
    }

    rotatePointAboutPosition([x, y], [rotX, rotY], angle) {
        return [
            (x - rotX) * Math.cos(angle) - (y - rotY) * Math.sin(angle) + rotX,
            (x - rotX) * Math.sin(angle) + (y - rotY) * Math.cos(angle) + rotY,
        ];
    }

    halftone({ angle, dotSize, dotResolution, targetCtx, sourceCtx, width, height, color, layer = false }) {
        const sourceImageData = sourceCtx.getImageData(0, 0, width, height);
        angle = (angle * Math.PI) / 180;
        
        // Enable anti-aliasing for smoother circles
        targetCtx.imageSmoothingEnabled = true;
        targetCtx.imageSmoothingQuality = 'high';
        
        if (!layer) {
            targetCtx.fillStyle = document.getElementById('backgroundColor').value;
            targetCtx.fillRect(0, 0, width, height);
        }
        
        targetCtx.fillStyle = color;

        // Get the four corners of the screen
        const tl = [0, 0];
        const tr = [width, 0];
        const br = [width, height];
        const bl = [0, height];

        // Rotate the screen, then find the minimum and maximum of the values
        const boundaries = [tl, br, tr, bl].map(([x, y]) => {
            return this.rotatePointAboutPosition([x, y], [width / 2, height / 2], angle);
        });

        const minX = Math.min(...boundaries.map((point) => point[0])) | 0;
        const minY = Math.min(...boundaries.map((point) => point[1])) | 0;
        const maxY = Math.max(...boundaries.map((point) => point[1])) | 0;
        const maxX = Math.max(...boundaries.map((point) => point[0])) | 0;

        for (let y = minY; y < maxY; y += dotResolution) {
            for (let x = minX; x < maxX; x += dotResolution) {
                let [rotatedX, rotatedY] = this.rotatePointAboutPosition(
                    [x, y],
                    [width / 2, height / 2],
                    -angle
                );

                if (rotatedX < 0 || rotatedY < 0 || rotatedX > width || rotatedY > height) {
                    continue;
                }

                const index = this.positionToDataIndex(
                    Math.floor(rotatedX),
                    Math.floor(rotatedY),
                    width
                );

                // Convert to grayscale using luminance formula
                const r = sourceImageData.data[index];
                const g = sourceImageData.data[index + 1];
                const b = sourceImageData.data[index + 2];
                const alpha = sourceImageData.data[index + 3];
                const value = (r * 0.299 + g * 0.587 + b * 0.114);

                if (alpha > 0) {
                    const circleRadius = this.map(value, 0, 255, dotSize / 2, 0);
                    
                    if (circleRadius > 0.1) { // Only draw circles with meaningful size
                        targetCtx.beginPath();
                        targetCtx.arc(rotatedX, rotatedY, circleRadius, 0, Math.PI * 2);
                        targetCtx.closePath();
                        targetCtx.fill();
                    }
                }
            }
        }
    }

    generateBasicHalftone() {
        const dotSize = parseInt(document.getElementById('dotSize').value);
        const dotResolution = parseInt(document.getElementById('dotResolution').value);
        const angle = parseInt(document.getElementById('angle').value);
        const color = document.getElementById('halftoneColor').value;

        this.halftone({
            angle: angle,
            dotSize: dotSize,
            dotResolution: dotResolution,
            targetCtx: this.targetCtx,
            sourceCtx: this.sourceCtx,
            width: this.sourceCanvas.width,
            height: this.sourceCanvas.height,
            color: color
        });
    }

    generateDuotone() {
        const dotSize = parseInt(document.getElementById('dotSize').value);
        const dotResolution = parseInt(document.getElementById('dotResolution').value);
        const angle = parseInt(document.getElementById('angle').value);

        // Create two layers - one for highlights, one for shadows
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = this.sourceCanvas.width;
        tempCanvas.height = this.sourceCanvas.height;

        // Layer 1: All values (light color)
        this.halftone({
            angle: angle + 15,
            dotSize: dotSize,
            dotResolution: dotResolution,
            targetCtx: this.targetCtx,
            sourceCtx: this.sourceCtx,
            width: this.sourceCanvas.width,
            height: this.sourceCanvas.height,
            color: '#8B4513' // Brown
        });

        // Create shadow layer
        const sourceImageData = this.sourceCtx.getImageData(0, 0, this.sourceCanvas.width, this.sourceCanvas.height);
        const shadowImageData = tempCtx.createImageData(this.sourceCanvas.width, this.sourceCanvas.height);

        for (let i = 0; i < sourceImageData.data.length; i += 4) {
            const r = sourceImageData.data[i];
            const g = sourceImageData.data[i + 1];
            const b = sourceImageData.data[i + 2];
            const value = (r * 0.299 + g * 0.587 + b * 0.114);
            
            if (value < 127) {
                const adjustedValue = this.map(value, 0, 127, 0, 255);
                shadowImageData.data[i] = adjustedValue;
                shadowImageData.data[i + 1] = adjustedValue;
                shadowImageData.data[i + 2] = adjustedValue;
                shadowImageData.data[i + 3] = 255;
            } else {
                shadowImageData.data[i] = 255;
                shadowImageData.data[i + 1] = 255;
                shadowImageData.data[i + 2] = 255;
                shadowImageData.data[i + 3] = 255;
            }
        }

        tempCtx.putImageData(shadowImageData, 0, 0);

        // Layer 2: Shadows (black)
        this.halftone({
            angle: angle,
            dotSize: dotSize,
            dotResolution: dotResolution,
            targetCtx: this.targetCtx,
            sourceCtx: tempCtx,
            width: this.sourceCanvas.width,
            height: this.sourceCanvas.height,
            color: '#000000',
            layer: true
        });
    }

    generateTritone() {
        const dotSize = parseInt(document.getElementById('dotSize').value);
        const dotResolution = parseInt(document.getElementById('dotResolution').value);
        const angle = parseInt(document.getElementById('angle').value);

        const colors = ['#FFD700', '#FF6347', '#000000']; // Gold, Tomato, Black
        const angles = [angle, angle + 30, angle + 60];

        colors.forEach((color, index) => {
            this.halftone({
                angle: angles[index],
                dotSize: dotSize,
                dotResolution: dotResolution,
                targetCtx: this.targetCtx,
                sourceCtx: this.sourceCtx,
                width: this.sourceCanvas.width,
                height: this.sourceCanvas.height,
                color: color,
                layer: index > 0
            });
        });
    }

    generateHalftone() {
        if (!this.currentImage) {
            alert('Please upload an image first.');
            return;
        }

        // Set up target canvas with high-resolution rendering
        const scaleFactor = 2; // Render at 2x resolution for smoother output
        const displayWidth = this.sourceCanvas.width;
        const displayHeight = this.sourceCanvas.height;
        
        // Set actual canvas size to higher resolution
        this.targetCanvas.width = displayWidth * scaleFactor;
        this.targetCanvas.height = displayHeight * scaleFactor;
        
        // Scale the context to match
        this.targetCtx.scale(scaleFactor, scaleFactor);
        
        // Set display size to normal
        this.targetCanvas.style.width = displayWidth + 'px';
        this.targetCanvas.style.height = displayHeight + 'px';

        const effectType = document.getElementById('effectType').value;

        // Add loading state
        document.getElementById('generateBtn').classList.add('loading');
        document.getElementById('generateBtn').textContent = 'Generating...';

        // Use setTimeout to allow UI to update
        setTimeout(() => {
            try {
                switch (effectType) {
                    case 'basic':
                        this.generateBasicHalftone();
                        break;
                    case 'duotone':
                        this.generateDuotone();
                        break;
                    case 'tritone':
                        this.generateTritone();
                        break;
                }

                // Show download and print buttons
                document.getElementById('downloadBtn').style.display = 'inline-block';
                document.getElementById('downloadBtn').classList.add('fade-in');
                document.getElementById('printBtn').style.display = 'inline-block';
                document.getElementById('printBtn').classList.add('fade-in');
            } catch (error) {
                console.error('Error generating halftone:', error);
                alert('An error occurred while generating the halftone. Please try again.');
            } finally {
                document.getElementById('generateBtn').classList.remove('loading');
                document.getElementById('generateBtn').textContent = 'Generate Halftone';
            }
        }, 100);
    }

    downloadResult() {
        if (!this.targetCanvas.width) {
            alert('Please generate a halftone first.');
            return;
        }

        const link = document.createElement('a');
        link.download = 'halftone-result.png';
        link.href = this.targetCanvas.toDataURL();
        link.click();
    }

    printResult() {
        if (!this.targetCanvas.width) {
            alert('Please generate a halftone first.');
            return;
        }

        // Create a new window for printing
        const printWindow = window.open('', '_blank');
        
        // Set up the print document
        printWindow.document.write(`
            <html>
                <head>
                    <title>Halftone Print</title>
                    <style>
                        @media print {
                            body {
                                margin: 0;
                                padding: 0;
                            }
                            img {
                                width: 100%;
                                height: auto;
                                max-width: 100vw;
                                max-height: 100vh;
                                object-fit: contain;
                            }
                        }
                    </style>
                </head>
                <body>
                    <img src="${this.targetCanvas.toDataURL()}" />
                    <script>
                        window.onload = function() {
                            window.print();
                            window.onafterprint = function() {
                                window.close();
                            };
                        };
                    </script>
                </body>
            </html>
        `);
        printWindow.document.close();
    }

    reset() {
        this.currentImage = null;
        this.sourceCtx.clearRect(0, 0, this.sourceCanvas.width, this.sourceCanvas.height);
        this.targetCtx.clearRect(0, 0, this.targetCanvas.width, this.targetCanvas.height);
        
        // Stop camera if active
        this.stopCamera();
        
        // Reset canvas transformations
        this.targetCtx.setTransform(1, 0, 0, 1, 0, 0);
        this.targetCanvas.style.width = '';
        this.targetCanvas.style.height = '';
        
        document.getElementById('controlsSection').style.display = 'none';
        document.getElementById('downloadBtn').style.display = 'none';
        document.getElementById('printBtn').style.display = 'none';
        document.getElementById('imageInput').value = '';

        // Reset controls to default values
        document.getElementById('dotSize').value = 5;
        document.getElementById('dotResolution').value = 3;
        document.getElementById('angle').value = 0;
        document.getElementById('halftoneColor').value = '#000000';
        document.getElementById('backgroundColor').value = '#ffffff';
        document.getElementById('effectType').value = 'basic';
        
        this.updateControlValues();
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HalftoneConverter();
});
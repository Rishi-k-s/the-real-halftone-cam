import React, { useState } from 'react';
import { Camera as CameraIcon, Loader } from 'lucide-react';
import apiService from '../../services/api.js';
import { showError, showSuccess, showLoading, dismissToast } from '../Toast/index.jsx';

const Camera = ({ onPhotoTaken, capturedImage }) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [cameraSettings, setCameraSettings] = useState({
    width: 1280,
    height: 720,
    camera_preference: 'auto'
  });

  const handleCapture = async () => {
    setIsCapturing(true);
    const toastId = showLoading('Capturing photo...');

    try {
      const response = await apiService.capturePhoto(cameraSettings);
      
      if (response.success) {
        // Get the captured image
        const imageBlob = await apiService.getLastPhoto();
        const imageUrl = URL.createObjectURL(imageBlob);
        
        onPhotoTaken(imageUrl, response.data);
        showSuccess('Photo captured successfully!');
      } else {
        showError(response.message || 'Failed to capture photo');
      }
    } catch (error) {
      showError('Camera error: ' + error.message);
    } finally {
      dismissToast(toastId);
      setIsCapturing(false);
    }
  };

  const handleSettingChange = (key, value) => {
    setCameraSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Camera Preview Area */}
        <div className="relative bg-gray-100 aspect-video flex items-center justify-center">
          {capturedImage ? (
            <img
              src={capturedImage}
              alt="Captured"
              className="max-w-full max-h-full object-contain"
            />
          ) : (
            <div className="text-center text-gray-500">
              <CameraIcon className="h-16 w-16 mx-auto mb-4" />
              <p className="text-lg">Ready to capture</p>
              <p className="text-sm">Click the shutter button below</p>
            </div>
          )}
        </div>

        {/* Camera Controls */}
        <div className="p-6 space-y-4">
          {/* Camera Settings */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Width
              </label>
              <select
                value={cameraSettings.width}
                onChange={(e) => handleSettingChange('width', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={isCapturing}
              >
                <option value={640}>640px</option>
                <option value={1280}>1280px</option>
                <option value={1920}>1920px</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Height
              </label>
              <select
                value={cameraSettings.height}
                onChange={(e) => handleSettingChange('height', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={isCapturing}
              >
                <option value={480}>480px</option>
                <option value={720}>720px</option>
                <option value={1080}>1080px</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Camera
              </label>
              <select
                value={cameraSettings.camera_preference}
                onChange={(e) => handleSettingChange('camera_preference', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={isCapturing}
              >
                <option value="auto">Auto</option>
                <option value="pi">Pi Camera</option>
                <option value="usb">USB Camera</option>
              </select>
            </div>
          </div>

          {/* Shutter Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={handleCapture}
              disabled={isCapturing}
              className="
                relative h-20 w-20 rounded-full border-4 border-gray-300 bg-white
                hover:border-primary-500 hover:bg-primary-50
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200 ease-in-out
                focus:outline-none focus:ring-4 focus:ring-primary-500/20
                active:scale-95
              "
            >
              <div className="
                absolute inset-2 rounded-full bg-primary-500 hover:bg-primary-600
                flex items-center justify-center transition-colors
              ">
                {isCapturing ? (
                  <Loader className="h-6 w-6 text-white animate-spin" />
                ) : (
                  <CameraIcon className="h-6 w-6 text-white" />
                )}
              </div>
            </button>
          </div>

          {/* Capture Info */}
          {capturedImage && (
            <div className="text-center text-sm text-gray-600 pt-2">
              Photo captured at {cameraSettings.width}×{cameraSettings.height}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Camera;

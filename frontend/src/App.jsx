import React, { useState, useEffect } from 'react';
import StepWizard from './components/StepWizard/index.jsx';
import Camera from './components/Camera/index.jsx';
import ParameterControls from './components/ParameterControls/index.jsx';
import ImageComparison from './components/ImageComparison/index.jsx';
import PrintControls from './components/PrintControls/index.jsx';
import Gallery from './components/Gallery/index.jsx';
import { ToastContainer, showError, showSuccess, showLoading, dismissToast } from './components/Toast/index.jsx';
import useImageCache from './hooks/useImageCache.js';
import apiService from './services/api.js';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [originalImage, setOriginalImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [captureData, setCaptureData] = useState(null);
  const [canProceed, setCanProceed] = useState(false);

  const { getCachedImage, setCachedImage, generateCacheKey } = useImageCache();

  // Update canProceed based on current step and available data
  useEffect(() => {
    switch (currentStep) {
      case 1: // Capture step
        setCanProceed(!!originalImage);
        break;
      case 2: // Process step
        setCanProceed(!!processedImage);
        break;
      case 3: // Print step
        setCanProceed(!!processedImage);
        break;
      case 4: // Gallery step
        setCanProceed(true);
        break;
      default:
        setCanProceed(false);
    }
  }, [currentStep, originalImage, processedImage]);

  const handleStepChange = (step) => {
    setCurrentStep(step);
  };

  const handlePhotoTaken = (imageUrl, data) => {
    setOriginalImage(imageUrl);
    setCaptureData(data);
    setProcessedImage(null); // Reset processed image when new photo is taken
    
    // Auto-advance to process step
    setTimeout(() => {
      setCurrentStep(2);
    }, 1000);
  };

  const handleParametersChange = async (parameters) => {
    if (!originalImage) {
      return;
    }

    // Check cache first
    const cacheKey = generateCacheKey(parameters);
    const cachedImage = getCachedImage(cacheKey);
    
    if (cachedImage) {
      setProcessedImage(cachedImage);
      return;
    }

    setIsProcessing(true);
    const toastId = showLoading('Processing image...');

    try {
      const response = await apiService.convertImage(parameters);
      
      if (response.success) {
        // Get the processed image
        const imageBlob = await apiService.getPreview();
        const imageUrl = URL.createObjectURL(imageBlob);
        
        setProcessedImage(imageUrl);
        setCachedImage(cacheKey, imageBlob);
        
        // Don't show success toast for real-time updates
      } else {
        showError(response.message || 'Failed to process image');
      }
    } catch (error) {
      showError('Processing error: ' + error.message);
    } finally {
      dismissToast(toastId);
      setIsProcessing(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <Camera
              onPhotoTaken={handlePhotoTaken}
              capturedImage={originalImage}
            />
          </div>
        );

      case 2:
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ImageComparison
                originalImage={originalImage}
                processedImage={processedImage}
                isProcessing={isProcessing}
              />
            </div>
            <div>
              <ParameterControls
                onParametersChange={handleParametersChange}
                isProcessing={isProcessing}
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <ImageComparison
              originalImage={originalImage}
              processedImage={processedImage}
              isProcessing={isProcessing}
            />
            <PrintControls
              processedImage={processedImage}
              hasProcessedImage={!!processedImage}
            />
          </div>
        );

      case 4:
        return <Gallery />;

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-sm">AC</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">ASCIICam</h1>
            </div>
            <div className="text-sm text-gray-500">
              Offline Camera & Print System
            </div>
          </div>
        </div>
      </header>

      {/* Step Wizard */}
      <StepWizard
        currentStep={currentStep}
        onStepChange={handleStepChange}
        canProceed={canProceed}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {renderStepContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="text-center text-sm text-gray-500">
            ASCIICam Frontend - Connected to backend at http://localhost:5000
          </div>
        </div>
      </footer>

      {/* Toast Container */}
      <ToastContainer />
    </div>
  );
}

export default App;

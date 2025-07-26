import React, { useState } from 'react';
import { Eye, EyeOff, ArrowLeftRight } from 'lucide-react';

const ImageComparison = ({ originalImage, processedImage, isProcessing }) => {
  const [showComparison, setShowComparison] = useState(true);
  const [viewMode, setViewMode] = useState('split'); // 'split', 'original', 'processed'

  const toggleComparison = () => {
    setShowComparison(!showComparison);
  };

  const cycleViewMode = () => {
    const modes = ['split', 'original', 'processed'];
    const currentIndex = modes.indexOf(viewMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setViewMode(modes[nextIndex]);
  };

  const getViewModeLabel = () => {
    switch (viewMode) {
      case 'original': return 'Original';
      case 'processed': return 'Processed';
      case 'split': return 'Split View';
      default: return 'Split View';
    }
  };

  if (!originalImage && !processedImage) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-500">
            <Eye className="h-12 w-12 mx-auto mb-2" />
            <p>No images to display</p>
            <p className="text-sm">Capture a photo to begin</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Controls Header */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Image Preview</h3>
          
          <div className="flex items-center space-x-2">
            {originalImage && processedImage && (
              <button
                onClick={cycleViewMode}
                className="flex items-center px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                <ArrowLeftRight className="h-4 w-4 mr-1" />
                {getViewModeLabel()}
              </button>
            )}
            
            <button
              onClick={toggleComparison}
              className="flex items-center px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              {showComparison ? (
                <>
                  <EyeOff className="h-4 w-4 mr-1" />
                  Hide
                </>
              ) : (
                <>
                  <Eye className="h-4 w-4 mr-1" />
                  Show
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Image Display Area */}
      {showComparison && (
        <div className="relative">
          {/* Processing Overlay */}
          {isProcessing && (
            <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Processing image...</p>
              </div>
            </div>
          )}

          {/* Split View */}
          {viewMode === 'split' && originalImage && processedImage && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
              <div className="relative">
                <img
                  src={originalImage}
                  alt="Original"
                  className="w-full h-auto object-contain bg-gray-100"
                />
                <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 text-xs rounded">
                  Original
                </div>
              </div>
              <div className="relative border-l md:border-l-2 border-gray-200">
                <img
                  src={processedImage}
                  alt="Processed"
                  className="w-full h-auto object-contain bg-gray-100"
                />
                <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 text-xs rounded">
                  Processed
                </div>
              </div>
            </div>
          )}

          {/* Single Image Views */}
          {viewMode === 'original' && originalImage && (
            <div className="relative">
              <img
                src={originalImage}
                alt="Original"
                className="w-full h-auto object-contain bg-gray-100"
              />
              <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 text-xs rounded">
                Original
              </div>
            </div>
          )}

          {viewMode === 'processed' && processedImage && (
            <div className="relative">
              <img
                src={processedImage}
                alt="Processed"
                className="w-full h-auto object-contain bg-gray-100"
              />
              <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 text-xs rounded">
                Processed
              </div>
            </div>
          )}

          {/* Fallback for single image */}
          {((viewMode === 'split' && (!originalImage || !processedImage)) || 
            (viewMode === 'original' && !originalImage) ||
            (viewMode === 'processed' && !processedImage)) && (
            <div className="aspect-video bg-gray-100 flex items-center justify-center">
              <div className="text-center text-gray-500">
                {originalImage || processedImage ? (
                  <div className="relative">
                    <img
                      src={originalImage || processedImage}
                      alt={originalImage ? "Original" : "Processed"}
                      className="max-w-full max-h-full object-contain"
                    />
                    <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 text-xs rounded">
                      {originalImage ? "Original" : "Processed"}
                    </div>
                  </div>
                ) : (
                  <>
                    <Eye className="h-12 w-12 mx-auto mb-2" />
                    <p>No image available</p>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Image Info Footer */}
      {showComparison && (originalImage || processedImage) && (
        <div className="p-3 bg-gray-50 border-t text-xs text-gray-600">
          <div className="flex justify-between items-center">
            <span>
              {viewMode === 'split' ? 'Side-by-side comparison' : 
               viewMode === 'original' ? 'Original image' : 'Processed image'}
            </span>
            {originalImage && processedImage && (
              <span className="text-green-600">✓ Ready for print</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageComparison;

import React, { useState, useEffect, useCallback } from 'react';
import { Settings, RotateCcw } from 'lucide-react';

const ParameterControls = ({ onParametersChange, isProcessing }) => {
  const [parameters, setParameters] = useState({
    mode: 'halftone',
    traditional: true,
    dot_size: 10,
    dot_resolution: 8,
    screen_angle: 45.0,
    invert: false,
    char_width: 80,
    font_size: 8,
  });

  // Debounced parameter change handler
  const debouncedOnChange = useCallback(
    debounce((params) => {
      onParametersChange(params);
    }, 300),
    [onParametersChange]
  );

  useEffect(() => {
    debouncedOnChange(parameters);
  }, [parameters, debouncedOnChange]);

  const handleParameterChange = (key, value) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const resetToDefaults = () => {
    setParameters({
      mode: 'halftone',
      traditional: true,
      dot_size: 10,
      dot_resolution: 8,
      screen_angle: 45.0,
      invert: false,
      char_width: 80,
      font_size: 8,
    });
  };

  const isHalftoneMode = parameters.mode === 'halftone';
  const isAsciiMode = parameters.mode === 'ascii';

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Settings className="h-5 w-5 text-gray-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Processing Parameters</h3>
        </div>
        <button
          onClick={resetToDefaults}
          disabled={isProcessing}
          className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
        >
          <RotateCcw className="h-4 w-4 mr-1" />
          Reset
        </button>
      </div>

      <div className="space-y-6">
        {/* Mode Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Processing Mode
          </label>
          <select
            value={parameters.mode}
            onChange={(e) => handleParameterChange('mode', e.target.value)}
            disabled={isProcessing}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="halftone">Halftone</option>
            <option value="ascii">ASCII Art</option>
          </select>
        </div>

        {/* Halftone Parameters */}
        {isHalftoneMode && (
          <div className="space-y-4">
            <div className="border-t pt-4">
              <h4 className="text-md font-medium text-gray-800 mb-3">Halftone Settings</h4>
              
              {/* Traditional Algorithm Toggle */}
              <div className="flex items-center justify-between mb-4">
                <label className="text-sm font-medium text-gray-700">
                  Traditional Algorithm
                </label>
                <button
                  type="button"
                  onClick={() => handleParameterChange('traditional', !parameters.traditional)}
                  disabled={isProcessing}
                  className={`
                    relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent 
                    transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${parameters.traditional ? 'bg-primary-600' : 'bg-gray-200'}
                  `}
                >
                  <span
                    className={`
                      pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 
                      transition duration-200 ease-in-out
                      ${parameters.traditional ? 'translate-x-5' : 'translate-x-0'}
                    `}
                  />
                </button>
              </div>

              {/* Dot Size Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dot Size: {parameters.dot_size}
                </label>
                <input
                  type="range"
                  min="3"
                  max="20"
                  step="1"
                  value={parameters.dot_size}
                  onChange={(e) => handleParameterChange('dot_size', parseInt(e.target.value))}
                  disabled={isProcessing}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Fine (3)</span>
                  <span>Coarse (20)</span>
                </div>
              </div>

              {/* Dot Resolution Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dot Resolution: {parameters.dot_resolution}
                </label>
                <input
                  type="range"
                  min="2"
                  max="15"
                  step="1"
                  value={parameters.dot_resolution}
                  onChange={(e) => handleParameterChange('dot_resolution', parseInt(e.target.value))}
                  disabled={isProcessing}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Dense (2)</span>
                  <span>Sparse (15)</span>
                </div>
              </div>

              {/* Screen Angle Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Screen Angle: {parameters.screen_angle}°
                </label>
                <input
                  type="range"
                  min="0"
                  max="89"
                  step="1"
                  value={parameters.screen_angle}
                  onChange={(e) => handleParameterChange('screen_angle', parseFloat(e.target.value))}
                  disabled={isProcessing}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0°</span>
                  <span>45°</span>
                  <span>89°</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ASCII Parameters */}
        {isAsciiMode && (
          <div className="space-y-4">
            <div className="border-t pt-4">
              <h4 className="text-md font-medium text-gray-800 mb-3">ASCII Settings</h4>
              
              {/* Character Width Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Character Width: {parameters.char_width}
                </label>
                <input
                  type="range"
                  min="40"
                  max="120"
                  step="10"
                  value={parameters.char_width}
                  onChange={(e) => handleParameterChange('char_width', parseInt(e.target.value))}
                  disabled={isProcessing}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Narrow (40)</span>
                  <span>Wide (120)</span>
                </div>
              </div>

              {/* Font Size Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Font Size: {parameters.font_size}px
                </label>
                <input
                  type="range"
                  min="6"
                  max="16"
                  step="1"
                  value={parameters.font_size}
                  onChange={(e) => handleParameterChange('font_size', parseInt(e.target.value))}
                  disabled={isProcessing}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Small (6)</span>
                  <span>Large (16)</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Common Parameters */}
        <div className="border-t pt-4">
          <h4 className="text-md font-medium text-gray-800 mb-3">Common Settings</h4>
          
          {/* Invert Toggle */}
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              Invert Colors
            </label>
            <button
              type="button"
              onClick={() => handleParameterChange('invert', !parameters.invert)}
              disabled={isProcessing}
              className={`
                relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent 
                transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                ${parameters.invert ? 'bg-primary-600' : 'bg-gray-200'}
              `}
            >
              <span
                className={`
                  pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 
                  transition duration-200 ease-in-out
                  ${parameters.invert ? 'translate-x-5' : 'translate-x-0'}
                `}
              />
            </button>
          </div>
        </div>

        {/* Processing Status */}
        {isProcessing && (
          <div className="border-t pt-4">
            <div className="flex items-center text-sm text-primary-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
              Processing image...
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Debounce utility function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export default ParameterControls;

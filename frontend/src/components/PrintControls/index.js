import React, { useState, useEffect } from 'react';
import { Printer, RefreshCw, Download } from 'lucide-react';
import apiService from '../../services/api';
import { showError, showSuccess, showLoading, dismissToast } from '../Toast';

const PrintControls = ({ processedImage, hasProcessedImage }) => {
  const [printers, setPrinters] = useState([]);
  const [selectedPrinter, setSelectedPrinter] = useState('');
  const [printOptions, setPrintOptions] = useState({
    copies: 1,
    paperSize: 'A4',
    quality: 'normal'
  });
  const [isPrinting, setIsPrinting] = useState(false);
  const [isLoadingPrinters, setIsLoadingPrinters] = useState(false);

  // Load printers on component mount
  useEffect(() => {
    loadPrinters();
  }, []);

  const loadPrinters = async () => {
    setIsLoadingPrinters(true);
    try {
      const response = await apiService.getPrinters();
      if (response.success && response.data) {
        setPrinters(response.data);
        // Auto-select first printer if available
        if (response.data.length > 0) {
          setSelectedPrinter(response.data[0].name || response.data[0]);
        }
      } else {
        showError('Failed to load printers');
        setPrinters([]);
      }
    } catch (error) {
      showError('Error loading printers: ' + error.message);
      setPrinters([]);
    } finally {
      setIsLoadingPrinters(false);
    }
  };

  const handlePrint = async () => {
    if (!selectedPrinter) {
      showError('Please select a printer');
      return;
    }

    if (!hasProcessedImage) {
      showError('No processed image to print');
      return;
    }

    setIsPrinting(true);
    const toastId = showLoading('Sending to printer...');

    try {
      const response = await apiService.printImage(selectedPrinter, printOptions);
      
      if (response.success) {
        showSuccess(`Print job sent to ${selectedPrinter}`);
      } else {
        showError(response.message || 'Failed to print');
      }
    } catch (error) {
      showError('Print error: ' + error.message);
    } finally {
      dismissToast(toastId);
      setIsPrinting(false);
    }
  };

  const handleDownload = () => {
    if (!processedImage) {
      showError('No processed image to download');
      return;
    }

    try {
      // Create download link
      const link = document.createElement('a');
      link.href = processedImage;
      link.download = `asciicam-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      showSuccess('Image downloaded successfully');
    } catch (error) {
      showError('Download failed: ' + error.message);
    }
  };

  const handleOptionChange = (key, value) => {
    setPrintOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Printer className="h-5 w-5 text-gray-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Print & Export</h3>
            </div>
            <button
              onClick={loadPrinters}
              disabled={isLoadingPrinters}
              className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-1 ${isLoadingPrinters ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Printer Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Printer
            </label>
            {isLoadingPrinters ? (
              <div className="flex items-center py-2 text-sm text-gray-500">
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Loading printers...
              </div>
            ) : printers.length > 0 ? (
              <select
                value={selectedPrinter}
                onChange={(e) => setSelectedPrinter(e.target.value)}
                disabled={isPrinting}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <option value="">Choose a printer...</option>
                {printers.map((printer, index) => (
                  <option key={index} value={printer.name || printer}>
                    {printer.name || printer}
                    {printer.status && ` (${printer.status})`}
                  </option>
                ))}
              </select>
            ) : (
              <div className="text-sm text-gray-500 py-2">
                No printers found. Make sure CUPS is running and printers are configured.
              </div>
            )}
          </div>

          {/* Print Options */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Copies
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={printOptions.copies}
                onChange={(e) => handleOptionChange('copies', parseInt(e.target.value) || 1)}
                disabled={isPrinting}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Paper Size
              </label>
              <select
                value={printOptions.paperSize}
                onChange={(e) => handleOptionChange('paperSize', e.target.value)}
                disabled={isPrinting}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <option value="A4">A4</option>
                <option value="Letter">Letter</option>
                <option value="A3">A3</option>
                <option value="A5">A5</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quality
              </label>
              <select
                value={printOptions.quality}
                onChange={(e) => handleOptionChange('quality', e.target.value)}
                disabled={isPrinting}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <option value="draft">Draft</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <button
              onClick={handlePrint}
              disabled={!hasProcessedImage || !selectedPrinter || isPrinting || isLoadingPrinters}
              className="
                flex-1 flex items-center justify-center px-4 py-3 bg-primary-600 hover:bg-primary-700 
                text-white font-medium rounded-md transition-colors
                disabled:opacity-50 disabled:cursor-not-allowed
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              "
            >
              {isPrinting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Printing...
                </>
              ) : (
                <>
                  <Printer className="h-4 w-4 mr-2" />
                  Print Image
                </>
              )}
            </button>

            <button
              onClick={handleDownload}
              disabled={!hasProcessedImage}
              className="
                flex-1 flex items-center justify-center px-4 py-3 bg-gray-600 hover:bg-gray-700 
                text-white font-medium rounded-md transition-colors
                disabled:opacity-50 disabled:cursor-not-allowed
                focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
              "
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </button>
          </div>

          {/* Status Messages */}
          {!hasProcessedImage && (
            <div className="text-center text-sm text-gray-500 py-2">
              Process an image before printing
            </div>
          )}

          {hasProcessedImage && !selectedPrinter && printers.length > 0 && (
            <div className="text-center text-sm text-amber-600 py-2">
              Select a printer to enable printing
            </div>
          )}

          {printers.length === 0 && !isLoadingPrinters && (
            <div className="text-center text-sm text-red-600 py-2">
              No printers available. Check CUPS configuration.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PrintControls;

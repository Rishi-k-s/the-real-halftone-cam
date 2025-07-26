import React, { useState, useEffect } from 'react';
import { Image, ChevronLeft, ChevronRight, RefreshCw, Calendar, Camera, Settings } from 'lucide-react';
import apiService from '../../services/api.js';
import { showError } from '../Toast/index.jsx';

const Gallery = () => {
  const [history, setHistory] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'captures', 'processed'

  const itemsPerPage = 12;

  useEffect(() => {
    loadHistory();
  }, [currentPage, filter]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getHistory(currentPage, itemsPerPage);
      
      if (response.success && response.data) {
        let filteredData = response.data;
        
        // Apply filter
        if (filter !== 'all') {
          filteredData = response.data.filter(item => {
            if (filter === 'captures') return item.type === 'capture';
            if (filter === 'processed') return item.type === 'processed';
            return true;
          });
        }
        
        setHistory(filteredData);
        setTotalPages(Math.ceil(filteredData.length / itemsPerPage) || 1);
      } else {
        setHistory([]);
        setTotalPages(1);
      }
    } catch (error) {
      showError('Failed to load history: ' + error.message);
      setHistory([]);
      setTotalPages(1);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handleImageClick = (item) => {
    setSelectedImage(item);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const formatTimestamp = (timestamp) => {
    try {
      // Parse timestamp format: YYYYMMDD_HHMMSS
      const year = timestamp.slice(0, 4);
      const month = timestamp.slice(4, 6);
      const day = timestamp.slice(6, 8);
      const hour = timestamp.slice(9, 11);
      const minute = timestamp.slice(11, 13);
      
      return `${day}/${month}/${year} ${hour}:${minute}`;
    } catch (error) {
      return timestamp;
    }
  };

  const getImageUrl = (item) => {
    const baseUrl = 'http://localhost:5000';
    if (item.type === 'capture') {
      return `${baseUrl}/static/history/captures/capture_${item.timestamp}.jpg`;
    } else {
      return `${baseUrl}/static/history/processed/${item.mode}_${item.timestamp}.png`;
    }
  };

  const getTypeIcon = (type) => {
    return type === 'capture' ? Camera : Settings;
  };

  const getTypeColor = (type) => {
    return type === 'capture' ? 'text-blue-600' : 'text-green-600';
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b bg-gray-50">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center">
              <Image className="h-5 w-5 text-gray-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Image Gallery</h3>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Filter */}
              <select
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Images</option>
                <option value="captures">Captures Only</option>
                <option value="processed">Processed Only</option>
              </select>
              
              {/* Refresh */}
              <button
                onClick={loadHistory}
                disabled={isLoading}
                className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Gallery Grid */}
        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <RefreshCw className="h-8 w-8 animate-spin text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Loading images...</p>
              </div>
            </div>
          ) : history.length > 0 ? (
            <>
              {/* Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                {history.map((item, index) => {
                  const TypeIcon = getTypeIcon(item.type);
                  return (
                    <div
                      key={`${item.type}-${item.timestamp}-${index}`}
                      className="
                        relative group cursor-pointer bg-gray-100 rounded-lg overflow-hidden
                        hover:shadow-lg transition-all duration-200 aspect-square
                      "
                      onClick={() => handleImageClick(item)}
                    >
                      <img
                        src={getImageUrl(item)}
                        alt={`${item.type} ${item.timestamp}`}
                        className="w-full h-full object-cover"
                        loading="lazy"
                        onError={(e) => {
                          e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIxIDNINUMzLjkgMyAzIDMuOSAzIDVWMTlDMyAyMC4xIDMuOSAyMSA1IDIxSDIxQzIyLjEgMjEgMjMgMjAuMSAyMyAxOVY1QzIzIDMuOSAyMi4xIDMgMjEgM1pNNSA1SDIxVjE5SDVWNVoiIGZpbGw9IiNEMUQ1REIiLz4KPC9zdmc+';
                        }}
                      />
                      
                      {/* Overlay */}
                      <div className="
                        absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 
                        transition-all duration-200 flex items-center justify-center
                      ">
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <TypeIcon className={`h-6 w-6 text-white`} />
                        </div>
                      </div>
                      
                      {/* Type Badge */}
                      <div className="absolute top-1 left-1">
                        <div className={`
                          inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium
                          ${item.type === 'capture' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}
                        `}>
                          <TypeIcon className="h-3 w-3 mr-1" />
                          {item.type}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center space-x-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="
                      flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md
                      hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    Previous
                  </button>
                  
                  <span className="px-3 py-2 text-sm text-gray-700">
                    Page {currentPage} of {totalPages}
                  </span>
                  
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="
                      flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md
                      hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  >
                    Next
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No images found</p>
              <p className="text-sm text-gray-400">Start by capturing a photo</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal for enlarged view */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-full overflow-auto">
            {/* Modal Header */}
            <div className="p-4 border-b flex items-center justify-between">
              <div className="flex items-center">
                {React.createElement(getTypeIcon(selectedImage.type), {
                  className: `h-5 w-5 mr-2 ${getTypeColor(selectedImage.type)}`
                })}
                <h4 className="text-lg font-semibold">
                  {selectedImage.type === 'capture' ? 'Captured Photo' : 'Processed Image'}
                </h4>
              </div>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600 text-xl font-bold"
              >
                ×
              </button>
            </div>
            
            {/* Modal Content */}
            <div className="p-4">
              <img
                src={getImageUrl(selectedImage)}
                alt={`${selectedImage.type} ${selectedImage.timestamp}`}
                className="max-w-full h-auto mx-auto"
              />
              
              {/* Image Details */}
              <div className="mt-4 text-sm text-gray-600 space-y-1">
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  {formatTimestamp(selectedImage.timestamp)}
                </div>
                
                {selectedImage.type === 'processed' && selectedImage.parameters && (
                  <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                    <strong>Parameters:</strong>
                    <pre className="mt-1 whitespace-pre-wrap">
                      {JSON.stringify(selectedImage.parameters, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gallery;

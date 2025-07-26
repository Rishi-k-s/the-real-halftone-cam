import { useState, useCallback } from 'react';

const useImageCache = () => {
  const [cache, setCache] = useState(new Map());

  const getCachedImage = useCallback((key) => {
    return cache.get(key);
  }, [cache]);

  const setCachedImage = useCallback((key, imageBlob) => {
    setCache(prev => {
      const newCache = new Map(prev);
      // Create object URL for the blob
      const imageUrl = URL.createObjectURL(imageBlob);
      newCache.set(key, imageUrl);
      
      // Clean up old URLs to prevent memory leaks
      if (prev.has(key)) {
        URL.revokeObjectURL(prev.get(key));
      }
      
      return newCache;
    });
  }, []);

  const clearCache = useCallback(() => {
    // Clean up all object URLs
    cache.forEach(url => URL.revokeObjectURL(url));
    setCache(new Map());
  }, [cache]);

  const generateCacheKey = useCallback((params) => {
    return JSON.stringify(params);
  }, []);

  return {
    getCachedImage,
    setCachedImage,
    clearCache,
    generateCacheKey,
  };
};

export default useImageCache;

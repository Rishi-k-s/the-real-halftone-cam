import os
import cv2
import time
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self):
        self.pi_camera = None
        self.usb_camera = None
        self.active_camera = None
        self.camera_type = None
        
    def _try_pi_camera(self, width: int = 1280, height: int = 720) -> bool:
        """Try to initialize Raspberry Pi camera using picamzero"""
        try:
            from picamzero import Camera
            
            # Initialize the camera
            self.pi_camera = Camera()
            
            # Set resolution if supported
            try:
                self.pi_camera.resolution = (width, height)
            except AttributeError:
                # Some versions might not support direct resolution setting
                logger.info("Resolution setting not supported, using default")
            
            # Test the camera by starting preview briefly
            self.pi_camera.start_preview()
            time.sleep(1)  # Brief warm-up
            self.pi_camera.stop_preview()
            
            self.active_camera = self.pi_camera
            self.camera_type = "pi_camera"
            logger.info(f"Pi Camera initialized successfully with picamzero")
            return True
                
        except Exception as e:
            logger.warning(f"Failed to initialize Pi Camera: {str(e)}")
            self._cleanup_pi_camera()
            return False
    
    def _try_usb_camera(self, width: int = 1280, height: int = 720) -> bool:
        """Try to initialize USB camera"""
        try:
            # Try different camera indices
            for camera_index in range(4):
                try:
                    camera = cv2.VideoCapture(camera_index)
                    if not camera.isOpened():
                        camera.release()
                        continue
                    
                    # Set resolution
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    
                    # Test capture
                    ret, frame = camera.read()
                    if ret and frame is not None and frame.size > 0:
                        self.usb_camera = camera
                        self.active_camera = camera
                        self.camera_type = "usb_camera"
                        logger.info(f"USB Camera {camera_index} initialized successfully at {width}x{height}")
                        return True
                    else:
                        camera.release()
                        
                except Exception as e:
                    logger.debug(f"Camera index {camera_index} failed: {str(e)}")
                    if 'camera' in locals():
                        camera.release()
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to initialize USB Camera: {str(e)}")
            return False
    
    def initialize_camera(self, width: int = 1280, height: int = 720, 
                         camera_preference: str = "auto") -> Dict[str, Any]:
        """
        Initialize camera with preference order
        
        Args:
            width: Image width
            height: Image height  
            camera_preference: "pi", "usb", or "auto"
        
        Returns:
            Dict with success status and camera info
        """
        self.cleanup()
        
        if camera_preference == "pi":
            # Try only Pi camera
            if self._try_pi_camera(width, height):
                return {
                    "success": True,
                    "camera_type": self.camera_type,
                    "resolution": (width, height),
                    "message": "Pi Camera initialized successfully"
                }
        elif camera_preference == "usb":
            # Try only USB camera
            if self._try_usb_camera(width, height):
                return {
                    "success": True,
                    "camera_type": self.camera_type,
                    "resolution": (width, height),
                    "message": "USB Camera initialized successfully"
                }
        else:
            # Auto mode: Try Pi camera first, then USB
            if self._try_pi_camera(width, height):
                return {
                    "success": True,
                    "camera_type": self.camera_type,
                    "resolution": (width, height),
                    "message": "Pi Camera initialized successfully"
                }
            elif self._try_usb_camera(width, height):
                return {
                    "success": True,
                    "camera_type": self.camera_type,
                    "resolution": (width, height),
                    "message": "USB Camera initialized successfully (Pi Camera not available)"
                }
        
        return {
            "success": False,
            "camera_type": None,
            "resolution": None,
            "message": "No camera available",
            "error": "Failed to initialize any camera"
        }
    
    def capture_photo(self, output_path: str = "photo.jpg") -> Dict[str, Any]:
        """
        Capture a photo using the active camera
        
        Args:
            output_path: Path to save the captured image
            
        Returns:
            Dict with capture status and metadata
        """
        if not self.active_camera:
            return {
                "success": False,
                "message": "No active camera",
                "error": "Camera not initialized"
            }
        
        try:
            timestamp = datetime.now().isoformat()
            
            if self.camera_type == "pi_camera":
                # Capture with Pi Camera using picamzero
                try:
                    # Take photo directly to file
                    self.pi_camera.take_photo(output_path)
                    
                    # Verify the file was created and get its properties
                    if os.path.exists(output_path):
                        # Get image dimensions using cv2
                        img = cv2.imread(output_path)
                        if img is not None:
                            height, width = img.shape[:2]
                            return {
                                "success": True,
                                "camera_type": self.camera_type,
                                "timestamp": timestamp,
                                "file_path": output_path,
                                "resolution": (width, height),
                                "message": "Photo captured successfully with Pi Camera"
                            }
                        else:
                            return {
                                "success": False,
                                "message": "Failed to read captured image",
                                "error": "Image file corrupt or unreadable"
                            }
                    else:
                        return {
                            "success": False,
                            "message": "Photo file not created",
                            "error": "take_photo did not create file"
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "message": "Failed to capture photo",
                        "error": f"picamzero error: {str(e)}"
                    }
                    
            elif self.camera_type == "usb_camera":
                # Capture with USB Camera
                ret, frame = self.usb_camera.read()
                
                if ret and frame is not None:
                    # Save image
                    success = cv2.imwrite(output_path, frame)
                    
                    if success:
                        return {
                            "success": True,
                            "camera_type": self.camera_type,
                            "timestamp": timestamp,
                            "file_path": output_path,
                            "resolution": (frame.shape[1], frame.shape[0]),  # (width, height)
                            "message": "Photo captured successfully with USB Camera"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Failed to save image",
                            "error": "Image write failed"
                        }
                else:
                    return {
                        "success": False,
                        "message": "Failed to capture frame",
                        "error": "Camera read failed"
                    }
            else:
                return {
                    "success": False,
                    "message": "Unknown camera type",
                    "error": f"Unsupported camera type: {self.camera_type}"
                }
            
        except Exception as e:
            logger.error(f"Capture error: {str(e)}")
            return {
                "success": False,
                "message": "Capture failed",
                "error": str(e)
            }
    
    def get_camera_status(self) -> Dict[str, Any]:
        """Get current camera status"""
        return {
            "active_camera": self.camera_type,
            "available": self.active_camera is not None,
            "pi_camera_available": self._test_pi_camera(),
            "usb_camera_available": self._test_usb_camera()
        }
    
    def _test_pi_camera(self) -> bool:
        """Test if Pi camera is available without initializing"""
        try:
            from picamzero import Camera
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def _test_usb_camera(self) -> bool:
        """Test if USB camera is available without initializing"""
        try:
            for i in range(2):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cap.release()
                    return True
            return False
        except Exception:
            return False
    
    def _cleanup_pi_camera(self):
        """Clean up Pi camera resources"""
        if self.pi_camera:
            try:
                # picamzero cameras don't need explicit cleanup like picamera2
                # Just ensure any preview is stopped
                self.pi_camera.stop_preview()
            except Exception:
                pass
            self.pi_camera = None
    
    def _cleanup_usb_camera(self):
        """Clean up USB camera resources"""
        if self.usb_camera:
            try:
                self.usb_camera.release()
            except Exception:
                pass
            self.usb_camera = None
    
    def cleanup(self):
        """Clean up all camera resources"""
        self._cleanup_pi_camera()
        self._cleanup_usb_camera()
        self.active_camera = None
        self.camera_type = None
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

# Global camera manager instance
camera_manager = CameraManager()

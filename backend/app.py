from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from pathlib import Path
from datetime import datetime
import uvicorn

# Import our modules
from camera import camera_manager
from halftone import halftone_processor, ascii_processor
from printer import printer_manager
from history import history_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ASCIICam Backend",
    description="Raspberry Pi Camera System with Halftone and ASCII Art Processing",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directories exist
os.makedirs("./static", exist_ok=True)
os.makedirs("./static/history", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request bodies
class CaptureRequest(BaseModel):
    width: Optional[int] = 1280
    height: Optional[int] = 720
    camera_preference: Optional[str] = "auto"  # "auto", "pi", "usb"

class ConvertRequest(BaseModel):
    mode: str  # "halftone" or "ascii"
    
    # Halftone parameters
    dot_size: Optional[int] = 8        # Maximum dot size (radius)
    dot_spacing: Optional[int] = 5     # Distance between dot centers (legacy, for compatibility)
    dot_resolution: Optional[int] = 5  # Distance between dot centers (new name)
    screen_angle: Optional[float] = 0.0 # Screen angle in degrees
    threshold: Optional[int] = 127      # Grayscale threshold (for compatibility)
    invert: Optional[bool] = False      # Invert halftone
    traditional: Optional[bool] = True  # Use traditional halftone algorithm (based on anderoonies implementation)
    
    # Legacy parameter (renamed for clarity)
    angle: Optional[float] = 0.0        # Deprecated: use screen_angle instead
    
    # ASCII parameters
    char_width: Optional[int] = 80      # For ASCII mode
    font_size: Optional[int] = 8        # For ASCII mode

class PrintRequest(BaseModel):
    printer_name: Optional[str] = None
    copies: Optional[int] = 1
    paper_size: Optional[str] = "A4"
    print_text: Optional[bool] = False  # For ASCII: print as text instead of image

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ASCIICam Backend API",
        "version": "1.0.0",
        "endpoints": {
            "POST /capture": "Capture a photo using camera",
            "POST /convert": "Convert photo to halftone or ASCII",
            "GET /preview": "Get the last processed image",
            "POST /print": "Print the last processed image",
            "GET /status": "Get system status",
            "GET /history": "Get processing history",
            "GET /printers": "Get available printers"
        }
    }

@app.post("/capture")
async def capture_photo(request: CaptureRequest):
    """Capture a photo using the camera"""
    try:
        # Initialize camera with specified settings
        init_result = camera_manager.initialize_camera(
            width=request.width or 1280,
            height=request.height or 720,
            camera_preference=request.camera_preference or "auto"
        )
        
        if not init_result["success"]:
            raise HTTPException(status_code=503, detail=init_result)
        
        # Capture photo
        capture_result = camera_manager.capture_photo("./static/photo.jpg")
        
        if capture_result["success"]:
            # Save to history
            history_result = history_manager.save_capture(
                "./static/photo.jpg", 
                capture_result
            )
            
            # Include history info in response
            if history_result["success"]:
                capture_result["history"] = history_result
            
            return JSONResponse(content=capture_result)
        else:
            raise HTTPException(status_code=500, detail=capture_result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Capture endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error during capture"
        })

@app.post("/capture/retry")
async def retry_capture(request: CaptureRequest):
    """Retry camera capture (same as /capture but explicit retry endpoint)"""
    return await capture_photo(request)

@app.post("/convert")
async def convert_image(request: ConvertRequest):
    """Convert the captured photo to halftone or ASCII art"""
    try:
        # Check if photo exists
        if not os.path.exists("./static/photo.jpg"):
            raise HTTPException(status_code=404, detail={
                "success": False,
                "error": "No photo to convert",
                "message": "Please capture a photo first"
            })
        
        if request.mode == "halftone":
            # Determine which parameters to use (new vs legacy)
            dot_resolution = request.dot_resolution or request.dot_spacing or 5
            screen_angle = request.screen_angle if request.screen_angle is not None else (request.angle or 0.0)
            
            # Choose halftone method
            if request.traditional:
                # Use traditional halftone algorithm (better quality)
                result = halftone_processor.generate_traditional_halftone(
                    image_path="./static/photo.jpg",
                    output_path="./static/preview.png",
                    dot_size=request.dot_size or 8,
                    dot_resolution=dot_resolution,
                    screen_angle=screen_angle,
                    invert=request.invert or False
                )
            else:
                # Use original halftone method
                result = halftone_processor.generate_halftone(
                    image_path="./static/photo.jpg",
                    output_path="./static/preview.png",
                    dot_size=request.dot_size or 8,
                    dot_resolution=dot_resolution,
                    screen_angle=screen_angle,
                    threshold=request.threshold or 127,
                    invert=request.invert or False
                )
        elif request.mode == "ascii":
            # Generate ASCII art with default values for None parameters
            result = ascii_processor.generate_ascii_art(
                image_path="./static/photo.jpg",
                output_path="./static/preview.png",
                char_width=request.char_width or 80,
                invert=request.invert or False,
                font_size=request.font_size or 8
            )
            # Also save text file for printing
            if result["success"] and "text_output_path" in result:
                import shutil
                shutil.copy2(result["text_output_path"], "./static/ascii.txt")
        else:
            raise HTTPException(status_code=400, detail={
                "success": False,
                "error": "Invalid mode",
                "message": "Mode must be 'halftone' or 'ascii'"
            })
        
        if result["success"]:
            # Save to history
            history_result = history_manager.save_processed(
                result["output_path"],
                result
            )
            
            # Include history info in response
            if history_result["success"]:
                result["history"] = history_result
            
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Convert endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error during conversion"
        })

@app.get("/preview")
async def get_preview():
    """Get the last processed image as preview"""
    try:
        preview_path = "./static/preview.png"
        if os.path.exists(preview_path):
            return FileResponse(
                preview_path,
                media_type="image/png",
                filename="preview.png"
            )
        else:
            raise HTTPException(status_code=404, detail={
                "success": False,
                "error": "No preview available",
                "message": "Please convert an image first"
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error getting preview"
        })

@app.post("/print")
async def print_image(request: PrintRequest):
    """Print the last processed image or ASCII text"""
    try:
        # Check what files are available
        preview_png = "./static/preview.png"
        ascii_txt = "./static/ascii.txt"
        
        if request.print_text and os.path.exists(ascii_txt):
            # Print ASCII as text
            result = printer_manager.print_text_file(
                ascii_txt,
                printer_name=request.printer_name,
                copies=request.copies or 1,
                font_size=8
            )
        elif os.path.exists(preview_png):
            # Print processed image
            result = printer_manager.print_image(
                preview_png,
                printer_name=request.printer_name,
                copies=request.copies or 1,
                paper_size=request.paper_size or "A4"
            )
        else:
            raise HTTPException(status_code=404, detail={
                "success": False,
                "error": "No file to print",
                "message": "Please process an image first"
            })
        
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Print endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error during printing"
        })

@app.get("/status")
async def get_status():
    """Get system status including camera and printer availability"""
    try:
        camera_status = camera_manager.get_camera_status()
        printer_status = printer_manager.get_available_printers()
        
        # Check file availability
        files_status = {
            "photo_available": os.path.exists("./static/photo.jpg"),
            "preview_available": os.path.exists("./static/preview.png"),
            "ascii_text_available": os.path.exists("./static/ascii.txt")
        }
        
        return JSONResponse(content={
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "camera": camera_status,
            "printers": printer_status,
            "files": files_status,
            "message": "System status retrieved successfully"
        })
        
    except Exception as e:
        logger.error(f"Status endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error getting status"
        })

@app.get("/printers")
async def get_printers():
    """Get available printers"""
    try:
        result = printer_manager.get_available_printers()
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Printers endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error getting printers"
        })

@app.get("/history")
async def get_history(category: str = "all"):
    """Get processing history"""
    try:
        result = history_manager.get_history_list(category)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"History endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error getting history"
        })

@app.get("/history/{filename}")
async def get_history_file(filename: str):
    """Get a specific file from history"""
    try:
        # Search in history directories
        for subdir in ["captures", "processed"]:
            file_path = Path(f"./static/history/{subdir}/{filename}")
            if file_path.exists():
                # Determine media type
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    media_type = f"image/{filename.split('.')[-1].lower()}"
                    if media_type == "image/jpg":
                        media_type = "image/jpeg"
                elif filename.lower().endswith('.txt'):
                    media_type = "text/plain"
                else:
                    media_type = "application/octet-stream"
                
                return FileResponse(
                    str(file_path),
                    media_type=media_type,
                    filename=filename
                )
        
        raise HTTPException(status_code=404, detail={
            "success": False,
            "error": "File not found",
            "message": f"History file {filename} not found"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History file endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error getting history file"
        })

@app.delete("/history/{filename}")
async def delete_history_file(filename: str):
    """Delete a specific file from history"""
    try:
        result = history_manager.delete_file(filename)
        
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=404, detail=result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete history endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error deleting history file"
        })

@app.delete("/history")
async def clear_history(category: str = "all"):
    """Clear history files"""
    try:
        result = history_manager.clear_history(category)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Clear history endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": str(e),
            "message": "Internal server error clearing history"
        })

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Not found",
            "message": "The requested resource was not found"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"Starting ASCIICam Backend on {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

import os
import shutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoryManager:
    """Manages capture and processing history"""
    
    def __init__(self, history_dir: str = "./static/history", max_files: int = 100):
        self.history_dir = Path(history_dir)
        self.max_files = max_files
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure history directories exist"""
        self.history_dir.mkdir(parents=True, exist_ok=True)
        (self.history_dir / "captures").mkdir(exist_ok=True)
        (self.history_dir / "processed").mkdir(exist_ok=True)
    
    def save_capture(self, source_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Save a captured photo to history"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            dest_path = self.history_dir / "captures" / filename
            
            # Copy file to history
            shutil.copy2(source_path, dest_path)
            
            # Save metadata
            metadata_file = dest_path.with_suffix('.json')
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Clean up old files if needed
            self._cleanup_old_files("captures")
            
            return {
                "success": True,
                "history_path": str(dest_path),
                "metadata_path": str(metadata_file),
                "timestamp": timestamp,
                "message": "Capture saved to history"
            }
            
        except Exception as e:
            logger.error(f"Error saving capture to history: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save capture to history"
            }
    
    def save_processed(self, source_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Save a processed image to history"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = metadata.get("mode", "processed")
            
            # Determine file extension
            source_ext = Path(source_path).suffix
            filename = f"{mode}_{timestamp}{source_ext}"
            dest_path = self.history_dir / "processed" / filename
            
            # Copy file to history
            shutil.copy2(source_path, dest_path)
            
            # Save metadata
            metadata_file = dest_path.with_suffix('.json')
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Also copy text file if it exists (for ASCII)
            if "text_output_path" in metadata:
                text_source = Path(metadata["text_output_path"])
                if text_source.exists():
                    text_dest = dest_path.with_suffix('.txt')
                    shutil.copy2(text_source, text_dest)
                    metadata["history_text_path"] = str(text_dest)
            
            # Clean up old files if needed
            self._cleanup_old_files("processed")
            
            return {
                "success": True,
                "history_path": str(dest_path),
                "metadata_path": str(metadata_file),
                "timestamp": timestamp,
                "message": f"{mode.title()} image saved to history"
            }
            
        except Exception as e:
            logger.error(f"Error saving processed image to history: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to save processed image to history"
            }
    
    def get_history_list(self, category: str = "all") -> Dict[str, Any]:
        """Get list of historical files"""
        try:
            files = []
            
            if category in ["all", "captures"]:
                captures_dir = self.history_dir / "captures"
                if captures_dir.exists():
                    for file_path in captures_dir.glob("*.jpg"):
                        metadata_path = file_path.with_suffix('.json')
                        metadata = {}
                        if metadata_path.exists():
                            import json
                            try:
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                            except Exception:
                                pass
                        
                        files.append({
                            "type": "capture",
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "timestamp": metadata.get("timestamp", ""),
                            "metadata": metadata
                        })
            
            if category in ["all", "processed"]:
                processed_dir = self.history_dir / "processed"
                if processed_dir.exists():
                    for file_path in processed_dir.glob("*.png"):
                        metadata_path = file_path.with_suffix('.json')
                        metadata = {}
                        if metadata_path.exists():
                            import json
                            try:
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                            except Exception:
                                pass
                        
                        files.append({
                            "type": "processed",
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "timestamp": metadata.get("timestamp", ""),
                            "mode": metadata.get("mode", "unknown"),
                            "metadata": metadata
                        })
            
            # Sort by timestamp (newest first)
            files.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return {
                "success": True,
                "files": files,
                "total_count": len(files),
                "category": category,
                "message": f"Found {len(files)} historical files"
            }
            
        except Exception as e:
            logger.error(f"Error getting history list: {str(e)}")
            return {
                "success": False,
                "files": [],
                "error": str(e),
                "message": "Failed to get history list"
            }
    
    def get_file_metadata(self, filename: str) -> Dict[str, Any]:
        """Get metadata for a specific historical file"""
        try:
            # Search in both captures and processed directories
            for subdir in ["captures", "processed"]:
                file_path = self.history_dir / subdir / filename
                metadata_path = file_path.with_suffix('.json')
                
                if file_path.exists() and metadata_path.exists():
                    import json
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    return {
                        "success": True,
                        "filename": filename,
                        "path": str(file_path),
                        "metadata": metadata,
                        "message": "Metadata retrieved successfully"
                    }
            
            return {
                "success": False,
                "filename": filename,
                "message": "File not found in history"
            }
            
        except Exception as e:
            logger.error(f"Error getting file metadata: {str(e)}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": "Failed to get file metadata"
            }
    
    def delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete a file from history"""
        try:
            deleted_files = []
            
            # Search in both captures and processed directories
            for subdir in ["captures", "processed"]:
                file_path = self.history_dir / subdir / filename
                metadata_path = file_path.with_suffix('.json')
                text_path = file_path.with_suffix('.txt')  # For ASCII files
                
                if file_path.exists():
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                
                if metadata_path.exists():
                    metadata_path.unlink()
                    deleted_files.append(str(metadata_path))
                
                if text_path.exists():
                    text_path.unlink()
                    deleted_files.append(str(text_path))
            
            if deleted_files:
                return {
                    "success": True,
                    "filename": filename,
                    "deleted_files": deleted_files,
                    "message": f"File {filename} deleted from history"
                }
            else:
                return {
                    "success": False,
                    "filename": filename,
                    "message": "File not found in history"
                }
                
        except Exception as e:
            logger.error(f"Error deleting file from history: {str(e)}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": "Failed to delete file from history"
            }
    
    def clear_history(self, category: str = "all") -> Dict[str, Any]:
        """Clear history files"""
        try:
            deleted_count = 0
            
            if category in ["all", "captures"]:
                captures_dir = self.history_dir / "captures"
                if captures_dir.exists():
                    for file_path in captures_dir.iterdir():
                        if file_path.is_file():
                            file_path.unlink()
                            deleted_count += 1
            
            if category in ["all", "processed"]:
                processed_dir = self.history_dir / "processed"
                if processed_dir.exists():
                    for file_path in processed_dir.iterdir():
                        if file_path.is_file():
                            file_path.unlink()
                            deleted_count += 1
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "category": category,
                "message": f"Cleared {deleted_count} files from {category} history"
            }
            
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clear history"
            }
    
    def _cleanup_old_files(self, subdir: str):
        """Remove old files if count exceeds maximum"""
        try:
            dir_path = self.history_dir / subdir
            if not dir_path.exists():
                return
            
            # Get all image files sorted by modification time (oldest first)
            files = list(dir_path.glob("*.jpg")) + list(dir_path.glob("*.png"))
            files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest files if we exceed the limit
            while len(files) > self.max_files:
                old_file = files.pop(0)
                try:
                    # Remove image file
                    old_file.unlink()
                    
                    # Remove associated metadata file
                    metadata_file = old_file.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    # Remove associated text file (for ASCII)
                    text_file = old_file.with_suffix('.txt')
                    if text_file.exists():
                        text_file.unlink()
                        
                    logger.info(f"Removed old history file: {old_file.name}")
                    
                except Exception as e:
                    logger.error(f"Error removing old file {old_file}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

# Global history manager instance
history_manager = HistoryManager()

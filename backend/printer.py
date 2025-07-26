import os
import subprocess
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrinterManager:
    """Manages printing functionality using CUPS"""
    
    def __init__(self):
        self.default_printer = None
        self._detect_printers()
    
    def _detect_printers(self):
        """Detect available printers"""
        try:
            result = subprocess.run(['lpstat', '-p'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    # Get first available printer as default
                    first_line = lines[0]
                    if 'printer' in first_line:
                        self.default_printer = first_line.split()[1]
                        logger.info(f"Default printer set to: {self.default_printer}")
                else:
                    logger.warning("No printers found")
            else:
                logger.warning("Failed to detect printers")
        except Exception as e:
            logger.error(f"Error detecting printers: {str(e)}")
    
    def get_available_printers(self) -> Dict[str, Any]:
        """Get list of available printers"""
        try:
            result = subprocess.run(['lpstat', '-p'], 
                                  capture_output=True, text=True, timeout=10)
            
            printers = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('printer'):
                        parts = line.split()
                        if len(parts) >= 2:
                            printer_name = parts[1]
                            status = ' '.join(parts[2:]) if len(parts) > 2 else "Unknown"
                            printers.append({
                                "name": printer_name,
                                "status": status,
                                "is_default": printer_name == self.default_printer
                            })
            
            return {
                "success": True,
                "printers": printers,
                "default_printer": self.default_printer,
                "message": f"Found {len(printers)} printer(s)"
            }
            
        except Exception as e:
            logger.error(f"Error getting printer list: {str(e)}")
            return {
                "success": False,
                "printers": [],
                "error": str(e),
                "message": "Failed to get printer list"
            }
    
    def print_image(self, file_path: str, printer_name: Optional[str] = None,
                   copies: int = 1, paper_size: str = "A4") -> Dict[str, Any]:
        """
        Print an image file
        
        Args:
            file_path: Path to image file to print
            printer_name: Name of printer (uses default if None)
            copies: Number of copies to print
            paper_size: Paper size (A4, Letter, etc.)
            
        Returns:
            Dict with print status and job info
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found",
                "message": f"File {file_path} does not exist"
            }
        
        printer = printer_name or self.default_printer
        if not printer:
            return {
                "success": False,
                "error": "No printer available",
                "message": "No printer specified and no default printer found"
            }
        
        try:
            # Build lp command
            cmd = [
                'lp',
                '-d', printer,
                '-n', str(copies),
                '-o', f'media={paper_size}',
                '-o', 'fit-to-page',
                file_path
            ]
            
            # Execute print command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extract job ID from output
                job_id = None
                if result.stdout:
                    # Output typically looks like: "request id is printer-123 (1 file(s))"
                    parts = result.stdout.split()
                    for i, part in enumerate(parts):
                        if part == "id" and i + 2 < len(parts):
                            job_id = parts[i + 2]
                            break
                
                return {
                    "success": True,
                    "job_id": job_id,
                    "printer": printer,
                    "file_path": file_path,
                    "copies": copies,
                    "paper_size": paper_size,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Print job submitted successfully to {printer}"
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown print error"
                return {
                    "success": False,
                    "error": error_msg,
                    "printer": printer,
                    "message": f"Print job failed: {error_msg}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Print command timeout",
                "message": "Print command timed out"
            }
        except Exception as e:
            logger.error(f"Print error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Print failed: {str(e)}"
            }
    
    def print_text_file(self, file_path: str, printer_name: Optional[str] = None,
                       copies: int = 1, font_size: int = 12) -> Dict[str, Any]:
        """
        Print a text file (for ASCII art)
        
        Args:
            file_path: Path to text file to print
            printer_name: Name of printer (uses default if None)
            copies: Number of copies to print
            font_size: Font size for text printing
            
        Returns:
            Dict with print status and job info
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found", 
                "message": f"File {file_path} does not exist"
            }
        
        printer = printer_name or self.default_printer
        if not printer:
            return {
                "success": False,
                "error": "No printer available",
                "message": "No printer specified and no default printer found"
            }
        
        try:
            # Build lp command for text files
            cmd = [
                'lp',
                '-d', printer,
                '-n', str(copies),
                '-o', 'cpi=12',  # Characters per inch
                '-o', 'lpi=8',   # Lines per inch
                '-o', f'font-size={font_size}',
                file_path
            ]
            
            # Execute print command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extract job ID from output
                job_id = None
                if result.stdout:
                    parts = result.stdout.split()
                    for i, part in enumerate(parts):
                        if part == "id" and i + 2 < len(parts):
                            job_id = parts[i + 2]
                            break
                
                return {
                    "success": True,
                    "job_id": job_id,
                    "printer": printer,
                    "file_path": file_path,
                    "copies": copies,
                    "font_size": font_size,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Text print job submitted successfully to {printer}"
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown print error"
                return {
                    "success": False,
                    "error": error_msg,
                    "printer": printer,
                    "message": f"Text print job failed: {error_msg}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Print command timeout",
                "message": "Print command timed out"
            }
        except Exception as e:
            logger.error(f"Text print error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Text print failed: {str(e)}"
            }
    
    def get_print_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a print job"""
        try:
            result = subprocess.run(['lpstat', '-o', job_id], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                return {
                    "success": True,
                    "job_id": job_id,
                    "status": result.stdout.strip(),
                    "message": "Job status retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "job_id": job_id,
                    "message": "Job not found or completed"
                }
                
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
                "message": "Failed to get job status"
            }
    
    def cancel_print_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a print job"""
        try:
            result = subprocess.run(['cancel', job_id], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "job_id": job_id,
                    "message": f"Print job {job_id} cancelled successfully"
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return {
                    "success": False,
                    "job_id": job_id,
                    "error": error_msg,
                    "message": f"Failed to cancel job: {error_msg}"
                }
                
        except Exception as e:
            logger.error(f"Error cancelling job: {str(e)}")
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
                "message": f"Failed to cancel job: {str(e)}"
            }

# Global printer manager instance
printer_manager = PrinterManager()

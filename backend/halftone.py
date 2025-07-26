import os
import math
import logging
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HalftoneProcessor:
    """Port of the JavaScript halftone algorithm to Python"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def map_value(value: float, min_a: float, max_a: float, min_b: float, max_b: float) -> float:
        """Map a value from one range to another"""
        return ((value - min_a) / (max_a - min_a)) * (max_b - min_b) + min_b
    
    @staticmethod
    def rotate_point_about_position(point: Tuple[float, float], 
                                  rotation_center: Tuple[float, float], 
                                  angle: float) -> Tuple[float, float]:
        """Rotate a point around another point by given angle (in radians)"""
        x, y = point
        rot_x, rot_y = rotation_center
        
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        new_x = (x - rot_x) * cos_angle - (y - rot_y) * sin_angle + rot_x
        new_y = (x - rot_x) * sin_angle + (y - rot_y) * cos_angle + rot_y
        
        return (new_x, new_y)
    
    def generate_halftone(self, image_path: str, output_path: str, 
                         dot_size: int = 8, dot_resolution: int = 5,
                         screen_angle: float = 0.0, threshold: int = 127,
                         invert: bool = False, 
                         # Legacy parameters for backward compatibility
                         dot_spacing: Optional[int] = None, angle: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate halftone image from input image
        
        Args:
            image_path: Path to input image
            output_path: Path to save halftone image
            dot_size: Maximum size (radius) of halftone dots
            dot_resolution: Distance between dot centers (spacing)
            screen_angle: Screen angle in degrees for halftone pattern
            threshold: Grayscale threshold (kept for API compatibility)
            invert: Whether to invert the halftone
            dot_spacing: Legacy parameter (use dot_resolution instead)
            angle: Legacy parameter (use screen_angle instead)
            
        Returns:
            Dict with processing status and metadata
        """
        # Handle legacy parameters
        if dot_spacing is not None:
            dot_resolution = dot_spacing
        if angle is not None:
            screen_angle = angle
        try:
            # Load and convert image to grayscale
            with Image.open(image_path) as img:
                # Convert to RGB first, then to grayscale
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                gray_img = img.convert('L')
                width, height = gray_img.size
                
                # Create numpy array from image
                img_array = np.array(gray_img)
                
                # Create output image with white background
                output_img = Image.new('RGB', (width, height), (255, 255, 255))
                draw = ImageDraw.Draw(output_img)
                
                # Convert angle to radians
                angle_rad = math.radians(screen_angle)
                
                # Calculate boundaries for rotated sampling
                corners = [(0, 0), (width, 0), (width, height), (0, height)]
                rotated_corners = [
                    self.rotate_point_about_position(corner, (width/2, height/2), angle_rad)
                    for corner in corners
                ]
                
                min_x = int(min(corner[0] for corner in rotated_corners))
                max_x = int(max(corner[0] for corner in rotated_corners))
                min_y = int(min(corner[1] for corner in rotated_corners))
                max_y = int(max(corner[1] for corner in rotated_corners))
                
                # Generate halftone dots
                for y in range(min_y, max_y, dot_resolution):
                    for x in range(min_x, max_x, dot_resolution):
                        # Rotate sampling point back to image coordinates
                        rotated_x, rotated_y = self.rotate_point_about_position(
                            (x, y), (width/2, height/2), -angle_rad
                        )
                        
                        # Check if point is within image bounds
                        if (rotated_x < 0 or rotated_y < 0 or 
                            rotated_x >= width or rotated_y >= height):
                            continue
                        
                        # Sample pixel value with bounds checking
                        pixel_x = max(0, min(width - 1, int(rotated_x)))
                        pixel_y = max(0, min(height - 1, int(rotated_y)))
                        pixel_value = img_array[pixel_y, pixel_x]
                        
                        # Calculate dot radius based on pixel brightness
                        # Map pixel value to circle radius (0 to dot_size/2)
                        if invert:
                            # Inverted: bright pixels = large dots
                            circle_radius = self.map_value(pixel_value, 0, 255, 0, dot_size / 2)
                        else:
                            # Normal: dark pixels = large dots
                            circle_radius = self.map_value(pixel_value, 0, 255, dot_size / 2, 0)
                        
                        # Draw dot if radius is significant
                        if circle_radius > 0.5:
                            # Use the original grid position for drawing (x, y from the loop)
                            # This maintains the regular grid pattern while sampling rotated positions
                            draw_x, draw_y = x, y
                            
                            # Only draw if the dot center is within output bounds
                            if (0 <= draw_x < width and 0 <= draw_y < height):
                                # Draw filled circle
                                bbox = [
                                    draw_x - circle_radius, draw_y - circle_radius,
                                    draw_x + circle_radius, draw_y + circle_radius
                                ]
                                try:
                                    draw.ellipse(bbox, fill='black')
                                except:
                                    # Skip if drawing fails
                                    continue
                
                # Save output image
                output_img.save(output_path, 'PNG', quality=95)
                
                return {
                    "success": True,
                    "mode": "halftone",
                    "input_path": image_path,
                    "output_path": output_path,
                    "parameters": {
                        "dot_size": dot_size,
                        "dot_resolution": dot_resolution,
                        "screen_angle": screen_angle,
                        "threshold": threshold,
                        "invert": invert,
                        # Include legacy parameters for compatibility
                        "dot_spacing": dot_resolution,  # Legacy compatibility
                        "angle": screen_angle          # Legacy compatibility
                    },
                    "output_size": (width, height),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Halftone image generated successfully"
                }
                
        except Exception as e:
            logger.error(f"Halftone generation error: {str(e)}")
            return {
                "success": False,
                "mode": "halftone",
                "error": str(e),
                "message": "Failed to generate halftone image"
            }
    
    def generate_traditional_halftone(self, image_path: str, output_path: str,
                                    dot_size: int = 10, dot_resolution: Optional[int] = None,
                                    screen_angle: float = 45.0, invert: bool = False) -> Dict[str, Any]:
        """
        Generate traditional halftone using algorithm based on anderoonies implementation
        
        Args:
            image_path: Path to input image
            output_path: Path to save halftone image  
            dot_size: Maximum diameter of halftone dots (pixels)
            dot_resolution: Distance between dot centers (pixels). If None, uses dot_size
            screen_angle: Screen angle in degrees
            invert: Whether to invert the halftone
            
        Returns:
            Dict with processing status and metadata
        """
        if dot_resolution is None:
            dot_resolution = dot_size
            
        try:
            # Load and convert image to grayscale
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to grayscale
                gray_img = img.convert('L')
                width, height = gray_img.size
                
                # Create numpy array for faster access
                img_array = np.array(gray_img)
                
                # Create output image with white background
                output_img = Image.new('RGB', (width, height), (255, 255, 255))
                draw = ImageDraw.Draw(output_img)
                
                # Convert angle to radians
                angle_rad = math.radians(screen_angle)
                
                # Calculate the rotated screen boundaries
                corners = [(0, 0), (width, 0), (width, height), (0, height)]
                center = (width / 2, height / 2)
                
                # Rotate all corners to find bounding box
                rotated_corners = []
                for corner in corners:
                    rotated = self.rotate_point_about_position(corner, center, angle_rad)
                    rotated_corners.append(rotated)
                
                min_x = int(min(point[0] for point in rotated_corners))
                max_x = int(max(point[0] for point in rotated_corners))
                min_y = int(min(point[1] for point in rotated_corners))
                max_y = int(max(point[1] for point in rotated_corners))
                
                # Iterate over the rotated grid
                for grid_y in range(min_y, max_y, dot_resolution):
                    for grid_x in range(min_x, max_x, dot_resolution):
                        # Rotate this grid position back to sample the original image
                        sample_x, sample_y = self.rotate_point_about_position(
                            (grid_x, grid_y), center, -angle_rad
                        )
                        
                        # Check if sample position is within image bounds
                        if (sample_x < 0 or sample_y < 0 or 
                            sample_x >= width or sample_y >= height):
                            continue
                        
                        # Sample the grayscale value (bounds-checked)
                        pixel_x = max(0, min(width - 1, int(sample_x)))
                        pixel_y = max(0, min(height - 1, int(sample_y)))
                        pixel_value = img_array[pixel_y, pixel_x]
                        
                        # Calculate circle radius based on brightness
                        # Map from [0, 255] to [dot_size/2, 0] for dark pixels = large dots
                        if invert:
                            circle_radius = self.map_value(pixel_value, 0, 255, 0, dot_size / 2)
                        else:
                            circle_radius = self.map_value(pixel_value, 0, 255, dot_size / 2, 0)
                        
                        # Draw the dot if radius is meaningful
                        if circle_radius > 0.5:
                            # Draw at the original grid position 
                            draw_x, draw_y = grid_x, grid_y
                            
                            # Only draw if center is reasonably within bounds
                            if (draw_x >= -dot_size and draw_y >= -dot_size and 
                                draw_x <= width + dot_size and draw_y <= height + dot_size):
                                
                                bbox = [
                                    draw_x - circle_radius, draw_y - circle_radius,
                                    draw_x + circle_radius, draw_y + circle_radius
                                ]
                                try:
                                    draw.ellipse(bbox, fill='black')
                                except:
                                    continue
                
                # Save the result
                output_img.save(output_path, 'PNG', quality=95)
                
                return {
                    "success": True,
                    "mode": "traditional_halftone",
                    "input_path": image_path,
                    "output_path": output_path,
                    "parameters": {
                        "dot_size": dot_size,
                        "dot_resolution": dot_resolution,
                        "screen_angle": screen_angle,
                        "invert": invert
                    },
                    "output_size": (width, height),
                    "timestamp": datetime.now().isoformat(),
                    "message": "Traditional halftone image generated successfully"
                }
                
        except Exception as e:
            logger.error(f"Traditional halftone generation error: {str(e)}")
            return {
                "success": False,
                "mode": "traditional_halftone",
                "error": str(e),
                "message": "Failed to generate traditional halftone image"
            }

class ASCIIProcessor:
    """ASCII art processor with image output"""
    
    def __init__(self):
        # ASCII character set from light to dark
        self.ascii_chars = " .:-=+*#%@"
        
    def generate_ascii_art(self, image_path: str, output_path: str,
                          char_width: int = 80, invert: bool = False,
                          font_size: int = 8) -> Dict[str, Any]:
        """
        Generate ASCII art and save as image
        
        Args:
            image_path: Path to input image
            output_path: Path to save ASCII image
            char_width: Width of ASCII art in characters
            invert: Whether to invert the ASCII mapping
            font_size: Font size for rendering ASCII to image
            
        Returns:
            Dict with processing status and metadata
        """
        try:
            # Load and convert image to grayscale
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                gray_img = img.convert('L')
                
                # Calculate dimensions maintaining aspect ratio
                original_width, original_height = gray_img.size
                aspect_ratio = original_height / original_width
                char_height = int(char_width * aspect_ratio * 0.5)  # 0.5 to account for character aspect ratio
                
                # Resize image to ASCII dimensions
                ascii_img = gray_img.resize((char_width, char_height), Image.Resampling.LANCZOS)
                pixels = np.array(ascii_img)
                
                # Convert pixels to ASCII characters
                ascii_chars = self.ascii_chars
                if invert:
                    ascii_chars = ascii_chars[::-1]
                
                ascii_lines = []
                for row in pixels:
                    line = ""
                    for pixel in row:
                        # Map pixel value (0-255) to ASCII character index
                        char_index = int(self.map_value(pixel, 0, 255, 0, len(ascii_chars) - 1))
                        line += ascii_chars[char_index]
                    ascii_lines.append(line)
                
                # Render ASCII to image
                ascii_image = self._render_ascii_to_image(ascii_lines, font_size)
                ascii_image.save(output_path, 'PNG', quality=95)
                
                # Also save as text file
                text_output_path = output_path.replace('.png', '.txt')
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(ascii_lines))
                
                return {
                    "success": True,
                    "mode": "ascii",
                    "input_path": image_path,
                    "output_path": output_path,
                    "text_output_path": text_output_path,
                    "parameters": {
                        "char_width": char_width,
                        "char_height": char_height,
                        "invert": invert,
                        "font_size": font_size
                    },
                    "ascii_dimensions": (char_width, char_height),
                    "output_size": ascii_image.size,
                    "timestamp": datetime.now().isoformat(),
                    "message": "ASCII art generated successfully"
                }
                
        except Exception as e:
            logger.error(f"ASCII generation error: {str(e)}")
            return {
                "success": False,
                "mode": "ascii",
                "error": str(e),
                "message": "Failed to generate ASCII art"
            }
    
    def _render_ascii_to_image(self, ascii_lines: List[str], font_size: int = 8) -> Image.Image:
        """Render ASCII text to image"""
        # Try to load a monospace font
        try:
            # Try common monospace fonts
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                "/System/Library/Fonts/Monaco.ttf",  # macOS
                "C:/Windows/Fonts/consola.ttf",  # Windows
            ]
            
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            
            if font is None:
                font = ImageFont.load_default()
                
        except Exception:
            font = ImageFont.load_default()
        
        # Calculate image dimensions
        max_line_length = max(len(line) for line in ascii_lines) if ascii_lines else 1
        
        # Get text size using textbbox
        temp_img = Image.new('RGB', (1, 1), (255, 255, 255))
        temp_draw = ImageDraw.Draw(temp_img)
        
        try:
            # Try new method first
            bbox = temp_draw.textbbox((0, 0), 'M', font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older Pillow versions - use simple estimate
            char_width = font_size
            char_height = int(font_size * 1.2)
        
        img_width = int(max_line_length * char_width + 20)  # Add padding
        img_height = int(len(ascii_lines) * char_height + 20)  # Add padding
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw ASCII text
        y_offset = 10
        for line in ascii_lines:
            draw.text((10, y_offset), line, fill='black', font=font)
            y_offset += char_height
        
        return img
    
    @staticmethod
    def map_value(value: float, min_a: float, max_a: float, min_b: float, max_b: float) -> float:
        """Map a value from one range to another"""
        return ((value - min_a) / (max_a - min_a)) * (max_b - min_b) + min_b

# Processor instances
halftone_processor = HalftoneProcessor()
ascii_processor = ASCIIProcessor()

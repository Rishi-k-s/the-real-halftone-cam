#!/usr/bin/env python3

"""
Test script for ASCIICam conversion functions
"""

import os
import sys
import numpy as np
import cv2

# Add current directory to Python path
sys.path.append('.')

def create_test_image():
    """Create a simple test image"""
    print("📷 Creating test image...")
    
    # Create a test image with gradient and shapes
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    
    # Add gradient background
    for y in range(200):
        for x in range(300):
            intensity = int((x + y) / 2.0)
            img[y, x] = [intensity, intensity, intensity]
    
    # Add some shapes
    cv2.circle(img, (75, 75), 30, (255, 255, 255), -1)  # White circle
    cv2.rectangle(img, (150, 50), (250, 150), (128, 128, 128), -1)  # Gray rectangle
    
    # Save test image
    cv2.imwrite('./static/photo.jpg', img)
    print("✅ Test image saved to ./static/photo.jpg")

def test_halftone():
    """Test halftone conversion"""
    print("\n🎨 Testing halftone conversion...")
    
    try:
        from halftone import halftone_processor
        
        result = halftone_processor.generate_halftone(
            image_path="./static/photo.jpg",
            output_path="./static/test_halftone.png",
            dot_spacing=5,
            threshold=127,
            invert=False,
            angle=0.0
        )
        
        if result["success"]:
            print("✅ Halftone conversion successful!")
            print(f"   Output: {result['output_path']}")
            print(f"   Size: {result['output_size']}")
        else:
            print("❌ Halftone conversion failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        return result["success"]
        
    except Exception as e:
        print(f"❌ Halftone test failed with exception: {str(e)}")
        return False

def test_ascii():
    """Test ASCII art conversion"""
    print("\n📝 Testing ASCII conversion...")
    
    try:
        from halftone import ascii_processor
        
        result = ascii_processor.generate_ascii_art(
            image_path="./static/photo.jpg",
            output_path="./static/test_ascii.png",
            char_width=50,
            invert=False,
            font_size=8
        )
        
        if result["success"]:
            print("✅ ASCII conversion successful!")
            print(f"   Image output: {result['output_path']}")
            print(f"   Text output: {result.get('text_output_path', 'N/A')}")
            print(f"   ASCII size: {result['ascii_dimensions']}")
            
            # Show a preview of the ASCII text
            if result.get('text_output_path') and os.path.exists(result['text_output_path']):
                with open(result['text_output_path'], 'r') as f:
                    lines = f.readlines()[:5]  # First 5 lines
                print("   ASCII preview:")
                for line in lines:
                    print(f"   {line.rstrip()}")
                if len(lines) >= 5:
                    print("   ...")
        else:
            print("❌ ASCII conversion failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        return result["success"]
        
    except Exception as e:
        print(f"❌ ASCII test failed with exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 ASCIICam Conversion Tests")
    print("=" * 40)
    
    # Ensure directories exist
    os.makedirs('./static', exist_ok=True)
    
    # Create test image
    create_test_image()
    
    # Run tests
    halftone_ok = test_halftone()
    ascii_ok = test_ascii()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Halftone: {'✅ PASS' if halftone_ok else '❌ FAIL'}")
    print(f"   ASCII:    {'✅ PASS' if ascii_ok else '❌ FAIL'}")
    
    if halftone_ok and ascii_ok:
        print("\n🎉 All tests passed! The conversion system is working.")
        print("\n📁 Generated files:")
        for filename in ['test_halftone.png', 'test_ascii.png']:
            filepath = f'./static/{filename}'
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   {filename} ({size} bytes)")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

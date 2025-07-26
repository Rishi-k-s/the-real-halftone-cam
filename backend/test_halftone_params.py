#!/usr/bin/env python3

"""
Test script for enhanced halftone parameters
"""

import os
import sys
import numpy as np
import cv2
import json

# Add current directory to Python path
sys.path.append('.')

def create_test_image():
    """Create a test image with varying intensities"""
    print("📷 Creating test image for halftone testing...")
    
    # Create a test image with gradient and patterns
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # Create horizontal gradient
    for y in range(300):
        for x in range(400):
            intensity = int((x / 400.0) * 255)
            img[y, x] = [intensity, intensity, intensity]
    
    # Add some geometric shapes for interesting patterns
    cv2.circle(img, (100, 150), 60, (64, 64, 64), -1)    # Dark gray circle
    cv2.circle(img, (300, 150), 60, (192, 192, 192), -1) # Light gray circle
    cv2.rectangle(img, (150, 100), (250, 200), (128, 128, 128), -1)  # Medium gray rectangle
    
    # Save test image
    cv2.imwrite('./static/photo.jpg', img)
    print("✅ Test image saved to ./static/photo.jpg")

def test_halftone_parameters():
    """Test different halftone parameter combinations"""
    print("\n🎨 Testing enhanced halftone parameters...")
    
    try:
        from halftone import halftone_processor
        
        # Test cases with different parameter combinations
        test_cases = [
            {
                "name": "Small dots, tight spacing",
                "params": {"dot_size": 4, "dot_resolution": 3, "screen_angle": 0.0},
                "output": "./static/test_small_tight.png"
            },
            {
                "name": "Large dots, wide spacing",
                "params": {"dot_size": 12, "dot_resolution": 8, "screen_angle": 0.0},
                "output": "./static/test_large_wide.png"
            },
            {
                "name": "Medium dots, 45° angle",
                "params": {"dot_size": 8, "dot_resolution": 5, "screen_angle": 45.0},
                "output": "./static/test_45_angle.png"
            },
            {
                "name": "Small dots, 30° angle",
                "params": {"dot_size": 6, "dot_resolution": 4, "screen_angle": 30.0},
                "output": "./static/test_30_angle.png"
            },
            {
                "name": "Large dots, 15° angle, inverted",
                "params": {"dot_size": 10, "dot_resolution": 6, "screen_angle": 15.0, "invert": True},
                "output": "./static/test_inverted.png"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test {i}/5: {test_case['name']}")
            print(f"   Parameters: {test_case['params']}")
            
            result = halftone_processor.generate_halftone(
                image_path="./static/photo.jpg",
                output_path=test_case['output'],
                **test_case['params']
            )
            
            if result["success"]:
                print(f"   ✅ Success - Output: {os.path.basename(test_case['output'])}")
                
                # Check file size
                if os.path.exists(test_case['output']):
                    size = os.path.getsize(test_case['output'])
                    print(f"   📁 File size: {size} bytes")
                
                results.append({
                    "test": test_case['name'],
                    "success": True,
                    "output": test_case['output'],
                    "parameters_used": result["parameters"]
                })
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": result.get('error', 'Unknown error')
                })
        
        return results
        
    except Exception as e:
        print(f"❌ Halftone testing failed with exception: {str(e)}")
        return []

def test_api_compatibility():
    """Test API endpoint with new parameters"""
    print("\n🌐 Testing API compatibility...")
    
    import subprocess
    import time
    
    # Test data for API calls
    test_requests = [
        {
            "name": "New parameters",
            "data": {
                "mode": "halftone",
                "dot_size": 6,
                "dot_resolution": 4,
                "screen_angle": 22.5,
                "invert": False
            }
        },
        {
            "name": "Legacy parameters",
            "data": {
                "mode": "halftone",
                "dot_spacing": 5,
                "angle": 45.0,
                "invert": False
            }
        },
        {
            "name": "Mixed parameters (new should take precedence)",
            "data": {
                "mode": "halftone",
                "dot_size": 8,
                "dot_resolution": 6,
                "screen_angle": 60.0,
                "dot_spacing": 3,  # Should be ignored
                "angle": 30.0,     # Should be ignored
                "invert": False
            }
        }
    ]
    
    for i, test_req in enumerate(test_requests, 1):
        print(f"\n   API Test {i}/3: {test_req['name']}")
        
        # Create curl command
        data_json = json.dumps(test_req['data'])
        cmd = [
            'curl', '-s', '-X', 'POST', 'http://localhost:5000/convert',
            '-H', 'Content-Type: application/json',
            '-d', data_json
        ]
        
        try:
            # Check if server is running first
            check_cmd = ['curl', '-s', 'http://localhost:5000/status']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            
            if check_result.returncode != 0:
                print(f"   ⚠️ Server not running - skipping API test")
                continue
            
            # Run the actual test
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get("success"):
                        print(f"   ✅ API call successful")
                        params = response.get("parameters", {})
                        print(f"   📊 Used parameters: dot_size={params.get('dot_size')}, "
                              f"dot_resolution={params.get('dot_resolution')}, "
                              f"screen_angle={params.get('screen_angle')}")
                    else:
                        print(f"   ❌ API call failed: {response.get('message', 'Unknown error')}")
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
            else:
                print(f"   ❌ Curl command failed")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ API call timed out")
        except Exception as e:
            print(f"   ❌ API test error: {str(e)}")

def main():
    """Run all enhanced halftone tests"""
    print("🧪 Enhanced Halftone Parameter Tests")
    print("=" * 50)
    
    # Ensure directories exist
    os.makedirs('./static', exist_ok=True)
    
    # Create test image
    create_test_image()
    
    # Test halftone parameters
    results = test_halftone_parameters()
    
    # Test API compatibility
    test_api_compatibility()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    if results:
        success_count = sum(1 for r in results if r["success"])
        print(f"   Halftone tests: {success_count}/{len(results)} passed")
        
        if success_count == len(results):
            print("\n🎉 All halftone parameter tests passed!")
            print("\n📁 Generated test files:")
            for result in results:
                if result["success"] and os.path.exists(result["output"]):
                    filename = os.path.basename(result["output"])
                    size = os.path.getsize(result["output"])
                    print(f"   {filename} ({size} bytes) - {result['test']}")
        else:
            print(f"\n⚠️ {len(results) - success_count} tests failed")
    
    print(f"\n💡 New halftone parameters available:")
    print(f"   • dot_size: Maximum dot radius (1-20)")
    print(f"   • dot_resolution: Distance between dots (2-15)")
    print(f"   • screen_angle: Rotation angle in degrees (0-360)")
    print(f"   • Legacy parameters (dot_spacing, angle) still supported")
    
    return 0

if __name__ == "__main__":
    exit(main())

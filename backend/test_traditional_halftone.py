#!/usr/bin/env python3
"""
Test the enhanced traditional halftone algorithm
"""

import os
import sys
import requests
import json
from PIL import Image

# API base URL
BASE_URL = "http://localhost:8000"

def test_traditional_halftone():
    """Test the traditional halftone processing"""
    print("🧪 Testing Traditional Halftone Algorithm")
    print("=" * 50)
    
    # Check if photo exists
    if not os.path.exists("./static/photo.jpg"):
        print("❌ No photo found. Please capture a photo first or copy one to ./static/photo.jpg")
        return False
    
    # Test different traditional halftone configurations
    test_configs = [
        {
            "name": "Fine Dots (Small, Close)",
            "params": {
                "mode": "halftone",
                "traditional": True,
                "dot_size": 6,
                "dot_resolution": 4,
                "screen_angle": 45.0,
                "invert": False
            }
        },
        {
            "name": "Medium Dots (Classic)",
            "params": {
                "mode": "halftone", 
                "traditional": True,
                "dot_size": 10,
                "dot_resolution": 8,
                "screen_angle": 15.0,
                "invert": False
            }
        },
        {
            "name": "Large Dots (Bold)",
            "params": {
                "mode": "halftone",
                "traditional": True,
                "dot_size": 15,
                "dot_resolution": 12,
                "screen_angle": 0.0,
                "invert": False
            }
        },
        {
            "name": "Very Fine (Newspaper Style)",
            "params": {
                "mode": "halftone",
                "traditional": True,
                "dot_size": 4,
                "dot_resolution": 3,
                "screen_angle": 75.0,
                "invert": False
            }
        },
        {
            "name": "Inverted Fine",
            "params": {
                "mode": "halftone",
                "traditional": True,
                "dot_size": 8,
                "dot_resolution": 6,
                "screen_angle": 22.5,
                "invert": True
            }
        }
    ]
    
    results = []
    
    for i, config in enumerate(test_configs):
        print(f"\n🔄 Testing: {config['name']}")
        print(f"   Parameters: {config['params']}")
        
        try:
            # Make request to convert endpoint
            response = requests.post(f"{BASE_URL}/convert", json=config['params'])
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ Success: {result.get('message', 'Generated')}")
                    
                    # Save with different filename for comparison
                    output_filename = f"traditional_halftone_{i+1:02d}_{config['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}.png"
                    output_path = f"./static/{output_filename}"
                    
                    # Copy the preview to a named file
                    if os.path.exists("./static/preview.png"):
                        import shutil
                        shutil.copy2("./static/preview.png", output_path)
                        print(f"   💾 Saved as: {output_path}")
                        
                        # Check file size and dimensions
                        try:
                            img = Image.open(output_path)
                            print(f"   📏 Dimensions: {img.size}")
                            file_size = os.path.getsize(output_path) / 1024  # KB
                            print(f"   💿 File size: {file_size:.1f} KB")
                        except Exception as e:
                            print(f"   ⚠️  Could not read image info: {e}")
                    
                    results.append({
                        "config": config,
                        "result": result,
                        "output_file": output_filename,
                        "success": True
                    })
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                    results.append({
                        "config": config,
                        "result": result,
                        "success": False
                    })
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                results.append({
                    "config": config,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results.append({
                "config": config,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    successful = sum(1 for r in results if r.get("success"))
    print(f"✅ Successful: {successful}/{len(test_configs)}")
    print(f"❌ Failed: {len(test_configs) - successful}/{len(test_configs)}")
    
    if successful > 0:
        print(f"\n📁 Output files saved in ./static/")
        print("   Compare the results to see the effect of different parameters.")
        print("   Traditional halftone algorithm should produce classic dot patterns.")
    
    return successful > 0

def compare_algorithms():
    """Compare traditional vs original halftone algorithms"""
    print("\n🔄 Comparing Traditional vs Original Algorithms")
    print("=" * 50)
    
    comparison_params = {
        "mode": "halftone",
        "dot_size": 10,
        "dot_resolution": 8,
        "screen_angle": 45.0,
        "invert": False
    }
    
    # Test traditional
    print("Testing Traditional Algorithm...")
    traditional_params = {**comparison_params, "traditional": True}
    response = requests.post(f"{BASE_URL}/convert", json=traditional_params)
    
    if response.status_code == 200 and response.json().get("success"):
        import shutil
        shutil.copy2("./static/preview.png", "./static/comparison_traditional.png")
        print("✅ Traditional algorithm result saved as comparison_traditional.png")
    
    # Test original
    print("Testing Original Algorithm...")
    original_params = {**comparison_params, "traditional": False}
    response = requests.post(f"{BASE_URL}/convert", json=original_params)
    
    if response.status_code == 200 and response.json().get("success"):
        import shutil
        shutil.copy2("./static/preview.png", "./static/comparison_original.png")
        print("✅ Original algorithm result saved as comparison_original.png")
    
    print("\n🔍 Compare ./static/comparison_traditional.png vs ./static/comparison_original.png")
    print("   The traditional algorithm should show more accurate halftone patterns.")

if __name__ == "__main__":
    print("🚀 ASCIICam Traditional Halftone Testing")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the FastAPI server first.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the FastAPI server first:")
        print("   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Run tests
    success = test_traditional_halftone()
    
    if success:
        compare_algorithms()
        print("\n🎉 Testing completed! Check the output files for results.")
    else:
        print("\n❌ Testing failed. Check server logs for details.")

#!/usr/bin/env python3

"""
ASCIICam Halftone Parameter Examples
Shows how to use the enhanced halftone parameters for different effects
"""

import requests
import json
import time

def test_server():
    """Check if the ASCIICam server is running"""
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        return response.status_code == 200
    except:
        return False

def capture_photo():
    """Capture a test photo"""
    print("📷 Capturing test photo...")
    
    response = requests.post("http://localhost:5000/capture", 
                           json={"width": 800, "height": 600},
                           timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Photo captured: {result.get('resolution')}")
            return True
        else:
            print(f"❌ Capture failed: {result.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    return False

def test_halftone_effect(name, params, description):
    """Test a specific halftone effect"""
    print(f"\n🎨 Testing: {name}")
    print(f"   Description: {description}")
    print(f"   Parameters: {params}")
    
    response = requests.post("http://localhost:5000/convert",
                           json={"mode": "halftone", **params},
                           timeout=15)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Success! Output size: {result.get('output_size')}")
            used_params = result.get('parameters', {})
            print(f"   Used: dot_size={used_params.get('dot_size')}, "
                  f"dot_resolution={used_params.get('dot_resolution')}, "
                  f"screen_angle={used_params.get('screen_angle')}°")
            return True
        else:
            print(f"❌ Failed: {result.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    return False

def main():
    """Demonstrate halftone parameter usage"""
    print("🎯 ASCIICam Halftone Parameter Examples")
    print("=" * 45)
    
    if not test_server():
        print("❌ ASCIICam server is not running!")
        print("   Please start it with: ./run.sh")
        return 1
    
    print("✅ Server is running")
    
    # Capture a test photo first
    if not capture_photo():
        print("❌ Failed to capture photo. Using existing photo.jpg if available.")
    
    # Wait a moment
    time.sleep(1)
    
    # Test different halftone effects
    effects = [
        {
            "name": "Fine Detail",
            "params": {"dot_size": 3, "dot_resolution": 2, "screen_angle": 0},
            "description": "Small dots, tight spacing for fine detail"
        },
        {
            "name": "Bold Print",
            "params": {"dot_size": 12, "dot_resolution": 8, "screen_angle": 0},
            "description": "Large dots, wide spacing for bold effect"
        },
        {
            "name": "Classic Newspaper",
            "params": {"dot_size": 6, "dot_resolution": 4, "screen_angle": 45},
            "description": "Traditional 45° angle halftone"
        },
        {
            "name": "Artistic Angle",
            "params": {"dot_size": 8, "dot_resolution": 5, "screen_angle": 22.5},
            "description": "Custom angle for artistic effect"
        },
        {
            "name": "Inverted Pattern",
            "params": {"dot_size": 7, "dot_resolution": 5, "screen_angle": 15, "invert": True},
            "description": "Inverted halftone pattern"
        },
        {
            "name": "Dense Pattern",
            "params": {"dot_size": 4, "dot_resolution": 3, "screen_angle": 60},
            "description": "Dense dot pattern with 60° rotation"
        }
    ]
    
    successful_tests = 0
    
    for effect in effects:
        success = test_halftone_effect(
            effect["name"],
            effect["params"], 
            effect["description"]
        )
        if success:
            successful_tests += 1
        
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n" + "=" * 45)
    print(f"📊 Results: {successful_tests}/{len(effects)} effects generated successfully")
    
    if successful_tests > 0:
        print(f"\n✅ Preview available at: http://localhost:5000/preview")
        print(f"📚 Full API docs at: http://localhost:5000/docs")
    
    print(f"\n💡 Parameter Tips:")
    print(f"   • dot_size (1-20): Controls maximum dot radius")
    print(f"   • dot_resolution (2-15): Controls spacing between dots")
    print(f"   • screen_angle (0-360°): Rotates the halftone pattern")
    print(f"   • invert (true/false): Reverses light/dark pattern")
    print(f"   • Legacy parameters (dot_spacing, angle) still work")
    
    return 0 if successful_tests > 0 else 1

if __name__ == "__main__":
    exit(main())

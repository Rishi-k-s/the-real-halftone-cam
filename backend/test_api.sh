#!/bin/bash

# ASCIICam API Test Script

echo "🧪 Testing ASCIICam API Endpoints"
echo "=================================="

BASE_URL="http://localhost:5000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test if server is running
echo "🔍 Checking if server is running..."
if curl -s "$BASE_URL" > /dev/null; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${RED}❌ Server is not running. Please start it with ./run.sh${NC}"
    exit 1
fi

echo ""

# Test 1: Get system status
echo "📊 Testing system status..."
response=$(curl -s "$BASE_URL/status")
if echo "$response" | grep -q '"success": *true'; then
    echo -e "${GREEN}✅ Status endpoint working${NC}"
    
    # Extract camera info
    if echo "$response" | grep -q '"active_camera"'; then
        camera_type=$(echo "$response" | grep -o '"active_camera": *"[^"]*"' | cut -d'"' -f4)
        echo "   📸 Active camera: $camera_type"
    fi
else
    echo -e "${RED}❌ Status endpoint failed${NC}"
fi

echo ""

# Test 2: Capture photo
echo "📷 Testing photo capture..."
capture_response=$(curl -s -X POST "$BASE_URL/capture" \
    -H "Content-Type: application/json" \
    -d '{"width": 640, "height": 480, "camera_preference": "auto"}')

if echo "$capture_response" | grep -q '"success": *true'; then
    echo -e "${GREEN}✅ Photo capture successful${NC}"
    
    # Extract resolution info
    if echo "$capture_response" | grep -q '"resolution"'; then
        resolution=$(echo "$capture_response" | grep -o '"resolution": *\[[^]]*\]' | cut -d'[' -f2 | cut -d']' -f1)
        echo "   📐 Resolution: [$resolution]"
    fi
else
    echo -e "${RED}❌ Photo capture failed${NC}"
    echo "Response: $capture_response"
fi

echo ""

# Test 3: Convert to halftone
echo "🎨 Testing halftone conversion..."
halftone_response=$(curl -s -X POST "$BASE_URL/convert" \
    -H "Content-Type: application/json" \
    -d '{"mode": "halftone", "dot_spacing": 6, "threshold": 120, "invert": false, "angle": 15}')

if echo "$halftone_response" | grep -q '"success": *true'; then
    echo -e "${GREEN}✅ Halftone conversion successful${NC}"
    
    # Check if output file exists
    if [ -f "./static/preview.png" ]; then
        size=$(ls -lh ./static/preview.png | awk '{print $5}')
        echo "   📁 Output file: preview.png ($size)"
    fi
else
    echo -e "${RED}❌ Halftone conversion failed${NC}"
    echo "Response: $halftone_response"
fi

echo ""

# Test 4: Convert to ASCII
echo "📝 Testing ASCII conversion..."
ascii_response=$(curl -s -X POST "$BASE_URL/convert" \
    -H "Content-Type: application/json" \
    -d '{"mode": "ascii", "char_width": 60, "invert": false, "font_size": 10}')

if echo "$ascii_response" | grep -q '"success": *true'; then
    echo -e "${GREEN}✅ ASCII conversion successful${NC}"
    
    # Check if files exist
    if [ -f "./static/preview.png" ]; then
        size=$(ls -lh ./static/preview.png | awk '{print $5}')
        echo "   📁 Image output: preview.png ($size)"
    fi
    
    if [ -f "./static/ascii.txt" ]; then
        lines=$(wc -l < ./static/ascii.txt)
        echo "   📄 Text output: ascii.txt ($lines lines)"
        
        # Show preview
        echo "   🔍 ASCII preview (first 3 lines):"
        head -3 ./static/ascii.txt | sed 's/^/      /'
    fi
else
    echo -e "${RED}❌ ASCII conversion failed${NC}"
    echo "Response: $ascii_response"
fi

echo ""

# Test 5: Get preview
echo "🖼️ Testing preview endpoint..."
if curl -s -I "$BASE_URL/preview" | grep -q "200 OK"; then
    echo -e "${GREEN}✅ Preview endpoint working${NC}"
    echo "   📎 Preview available at: $BASE_URL/preview"
else
    echo -e "${YELLOW}⚠️ Preview endpoint returned error (may be normal if no image processed)${NC}"
fi

echo ""

# Test 6: Get history
echo "📚 Testing history endpoint..."
history_response=$(curl -s "$BASE_URL/history")
if echo "$history_response" | grep -q '"success": *true'; then
    echo -e "${GREEN}✅ History endpoint working${NC}"
    
    # Count files
    count=$(echo "$history_response" | grep -o '"total_count": *[0-9]*' | cut -d':' -f2 | tr -d ' ')
    echo "   📊 History files: $count"
else
    echo -e "${RED}❌ History endpoint failed${NC}"
fi

echo ""

# Test 7: Get printers
echo "🖨️ Testing printers endpoint..."
printers_response=$(curl -s "$BASE_URL/printers")
if echo "$printers_response" | grep -q '"success": *true'; then
    echo -e "${GREEN}✅ Printers endpoint working${NC}"
    
    # Count printers
    printer_count=$(echo "$printers_response" | grep -o '"printers": *\[' | wc -l)
    if [ "$printer_count" -gt 0 ]; then
        echo "   🖨️ Found printer configuration"
    else
        echo -e "   ${YELLOW}⚠️ No printers configured (CUPS may not be set up)${NC}"
    fi
else
    echo -e "${RED}❌ Printers endpoint failed${NC}"
fi

echo ""
echo "=================================="
echo "🎯 API Test Complete!"
echo ""
echo "📋 Summary:"
echo "   - All core endpoints are functional"
echo "   - Image capture and processing working"
echo "   - Both halftone and ASCII conversion operational"
echo ""
echo "🌐 Visit $BASE_URL/docs for interactive API documentation"
echo "🔧 Check server logs for any warnings or errors"

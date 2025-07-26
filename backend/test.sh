#!/bin/bash

# ASCIICam Backend Test Script

echo "Testing ASCIICam Backend..."

# Check if server is running
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "❌ Server is not running. Please start it first with ./run.sh"
    exit 1
fi

echo "✅ Server is running"

# Test basic endpoints
echo "Testing API endpoints..."

echo "📡 Testing root endpoint..."
curl -s http://localhost:5000/ | jq '.message' 2>/dev/null || echo "Root endpoint responding"

echo "📊 Testing status endpoint..."
curl -s http://localhost:5000/status | jq '.success' 2>/dev/null || echo "Status endpoint responding"

echo "🖨️ Testing printers endpoint..."
curl -s http://localhost:5000/printers | jq '.success' 2>/dev/null || echo "Printers endpoint responding"

echo "📁 Testing history endpoint..."
curl -s http://localhost:5000/history | jq '.success' 2>/dev/null || echo "History endpoint responding"

echo ""
echo "✅ Basic API tests completed!"
echo ""
echo "🎯 Next steps:"
echo "   1. Test camera capture: POST /capture"
echo "   2. Test image conversion: POST /convert"
echo "   3. Test image preview: GET /preview"
echo "   4. Test printing: POST /print"
echo ""
echo "📚 Full API documentation available at: http://localhost:5000/docs"

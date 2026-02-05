#!/bin/bash
# Integration tests for the system

echo "🧪 Running Integration Tests"
echo "============================="

BASE_URL="http://localhost:8000"

# Test health
echo ""
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s $BASE_URL/health)
if echo $HEALTH | grep -q "ok"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test list files (should be empty or existing)
echo ""
echo "2️⃣ Testing list files endpoint..."
FILES=$(curl -s $BASE_URL/files)
if [ $? -eq 0 ]; then
    echo "✅ List files passed"
else
    echo "❌ List files failed"
    exit 1
fi

# Test file upload
echo ""
echo "3️⃣ Testing file upload..."
UPLOAD=$(curl -s -X POST -F "file=@README.md" $BASE_URL/files)
if echo $UPLOAD | grep -q "id"; then
    FILE_ID=$(echo $UPLOAD | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    echo "✅ File uploaded with ID: $FILE_ID"
else
    echo "❌ File upload failed"
    exit 1
fi

# Test get file status
echo ""
echo "4️⃣ Testing get file status..."
STATUS=$(curl -s $BASE_URL/files/$FILE_ID)
if echo $STATUS | grep -q "status"; then
    echo "✅ Get file status passed"
else
    echo "❌ Get file status failed"
    exit 1
fi

echo ""
echo "✅ All integration tests passed!"

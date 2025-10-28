#!/bin/bash

# CarModX ngrok Launcher
# This script helps you share your CarModX project using ngrok

echo "🚀 CarModX ngrok Launcher"
echo "=========================="
echo ""

# Check if ngrok exists
if [ ! -f "./ngrok" ]; then
    echo "❌ Error: ngrok not found in current directory"
    echo "Please follow NGROK_GUIDE.md to install ngrok first"
    exit 1
fi

# Check if authtoken is configured
if ! ./ngrok config check &> /dev/null; then
    echo "⚠️  ngrok authtoken not configured"
    echo ""
    echo "Please run:"
    echo "  ./ngrok config add-authtoken YOUR_AUTHTOKEN_HERE"
    echo ""
    echo "Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Check if Django server is running
if ! curl -s http://127.0.0.1:8000 > /dev/null; then
    echo "⚠️  Django server not running on port 8000"
    echo ""
    echo "Please start Django server first:"
    echo "  python manage.py runserver 8000"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Django server is running"
echo "🌐 Starting ngrok tunnel..."
echo ""
echo "Press Ctrl+C to stop ngrok"
echo ""

# Start ngrok
./ngrok http 8000

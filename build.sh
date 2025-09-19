#!/bin/bash
# FinClick.AI Build Script for Vercel
echo "🚀 Starting FinClick.AI build process..."

# Navigate to frontend directory
cd frontend

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf build
rm -rf node_modules/.cache

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Check package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in frontend directory"
    exit 1
fi

# Set environment variables for build
export NODE_ENV=production
export REACT_APP_ENVIRONMENT=production
export GENERATE_SOURCEMAP=false
export CI=false

# Build the application
echo "🏗️  Building React application..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Error: Build directory not created"
    exit 1
fi

# Check if index.html exists
if [ ! -f "build/index.html" ]; then
    echo "❌ Error: index.html not found in build directory"
    exit 1
fi

echo "✅ Build completed successfully!"
echo "📁 Build directory contents:"
ls -la build/

echo "🎉 FinClick.AI is ready for deployment!"
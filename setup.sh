#!/bin/bash
# Setup script for Streamlit Cloud deployment

# Install system dependencies
apt-get update -qq
apt-get install -y -qq tesseract-ocr tesseract-ocr-eng libsm6 libxext6 libxrender-dev

echo "System dependencies installed."

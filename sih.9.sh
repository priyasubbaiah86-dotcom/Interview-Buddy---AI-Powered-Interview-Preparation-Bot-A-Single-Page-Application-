#!/bin/bash
echo "========================================"
echo "   Construction Progress AI"
echo "        OFFLINE DESKTOP APP"
echo "========================================"
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting Application..."
streamlit run app.py
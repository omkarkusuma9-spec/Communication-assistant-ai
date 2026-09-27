#!/bin/bash
# Push Communication Assistant & English Coach AI to GitHub

echo "Navigating to project directory..."
cd /f/My_Ai

echo "Staging all files..."
git add .

echo "Committing any updates..."
git commit -m "Initial commit: Communication Assistant & English Coach AI" 2>/dev/null || true

echo "Ensuring branch is main..."
git branch -M main

echo "Setting correct remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/omkarkusuma9-spec/Communication-assistant-ai.git

echo "Pushing code to GitHub..."
git push -u origin main

echo ""
echo "============================================="
echo "  SUCCESS! Refresh your GitHub page now:     "
echo "  https://github.com/omkarkusuma9-spec/Communication-assistant-ai"
echo "============================================="

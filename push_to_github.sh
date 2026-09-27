#!/bin/bash
# Push Communication Assistant & English Coach AI to GitHub

echo "Initializing Git repository..."
git init

echo "Staging files (excluding .env via .gitignore)..."
git add .

echo "Committing files..."
git commit -m "Initial commit: Communication Assistant & English Coach AI"

echo "Setting branch to main..."
git branch -M main

echo "Configuring remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/omkarkusuma9/omkarkusuma9-spec.git

echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Check your repository on GitHub."

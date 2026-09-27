@echo off
cd /d "F:\My_Ai"
echo Initializing Git repository...
git init

echo Staging files (excluding .env via .gitignore)...
git add .

echo Committing files...
git commit -m "Initial commit: Communication Assistant & English Coach AI"

git branch -M main

git remote remove origin 2>nul
git remote add origin https://github.com/omkarkusuma9/omkarkusuma9-spec.git

echo Pushing to GitHub...
git push -u origin main

pause

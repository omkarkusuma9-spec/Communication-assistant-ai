@echo off
cd /d "F:\My_Ai"
echo Staging files...
git add .
echo Committing...
git commit -m "Initial commit: Communication Assistant & English Coach AI" 2>nul
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/omkarkusuma9-spec/Communication-assistant-ai.git
echo Pushing to GitHub...
git push -u origin main
echo.
echo ============================================================
echo   Done! Refresh your GitHub page to see all your files!
echo ============================================================
pause

@echo off
title TerraPulse - GitHub Push & Vercel Deploy
echo ======================================================================
echo    TERRAPULSE - ONE-CLICK GITHUB PUSH & VERCEL DEPLOYMENT
echo    Target GitHub: https://github.com/DarkCrossDungen/never.give.up.git
echo    Target Vercel: https://terrapulse-gamma.vercel.app
echo ======================================================================
echo.

:: 1. Stage and commit all changes to Git
echo [1/3] Staging all files...
git add -A

echo [2/3] Committing changes...
git commit -m "feat: complete autonomous agronomy intelligence engine with dynamic pedology and zero api keys"

echo.
echo [3/3] Pushing to GitHub...
git push -u origin main

echo.
echo ======================================================================
echo    NOW DEPLOYING TO VERCEL PRODUCTION...
echo ======================================================================
vercel --prod --yes

echo.
echo ======================================================================
echo    SUCCESS! EVERYTHING IS LIVE!
echo    GitHub: https://github.com/DarkCrossDungen/never.give.up
echo    Vercel: https://terrapulse-gamma.vercel.app
echo ======================================================================
pause

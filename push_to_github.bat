@echo off
title Push TerraPulse to GitHub
echo ======================================================================
echo    TERRAPULSE - PUSHING FRESH REPOSITORY TO GITHUB
echo    Target: https://github.com/DarkCrossDungen/never.give.up.git
echo ======================================================================
echo.

:: Initialize local git if not already present
git init
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/DarkCrossDungen/never.give.up.git

echo Staging all project files...
git add -A

echo Creating fresh commit with current timestamp...
git commit -m "feat: complete TerraPulse agronomic diligence platform for NextStep Hacks 2026

- Responds directly to Earth Forward theme (sustainable agriculture, soil health, runoff elimination)
- Implements Zero-NIR Visible Optical Physics (VARI, ExG, GLI) via OpenCV 5.0
- Integrates real-time 3-depth soil hydrology & chemistry via Open-Meteo and ISRIC SoilGrids
- Powers cognitive diligence & stoichiometric fertilizer prescriptions via Autonomous Agronomy Engine
- Features Apple & Linear design system (light mode, SF Pro/Inter typography, 0 AI slop)
- Includes bank-grade PDF dossier export for agricultural lenders and cooperatives

Co-Authored-By: Claude Code <noreply@anthropic.com>"

echo.
echo Pushing fresh project to GitHub (updating all file timestamps to today)...
git push -u origin main --force

echo.
echo ======================================================================
echo    SUCCESS! Your project is now live on GitHub:
echo    https://github.com/DarkCrossDungen/never.give.up
echo ======================================================================
pause

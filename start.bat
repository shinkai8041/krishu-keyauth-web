@echo off
title KRISHU X AUTH — Sakura Cherry Blossom KeyAuth Server
color 0c
echo ===================================================
echo   KRISHU X AUTH — RED CHERRY BLOSSOM EDITION
echo ===================================================
echo.
python -m pip install -r requirements.txt
echo Starting server...
python app.py
pause

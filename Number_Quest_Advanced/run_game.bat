@echo off
cd /d "%~dp0"
py number_guessing.py
if errorlevel 1 pause

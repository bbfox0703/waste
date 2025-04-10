@echo off
echo Start GPU Server...
call .\gpu_env\Scripts\activate.bat
python translate_server.py

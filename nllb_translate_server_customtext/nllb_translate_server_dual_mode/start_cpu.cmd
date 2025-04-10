@echo off
echo Start CPU server....
call .\cpu_env\Scripts\activate.bat
python translate_server.py

@echo off
pip uninstall -y torch torchvision torchaudio
pip install torch transformers opencc-python-reimplemented flask flask-cors requests
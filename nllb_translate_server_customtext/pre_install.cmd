@echo off
rem 移當前版本的 PyTorch 和相關
pip uninstall -y torch torchvision torchaudio numpy
pip install virtualenv
pip install -r requirements_gpu.txt

rem 安裝最新的 PyTorch CPU 版本
rem pip install torch transformers opencc-python-reimplemented flask flask-cors requests

rem 如果您希望安裝 CUDA 版本的 GPU 模式 PyTorch，請使用以下指令：
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

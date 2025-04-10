@echo off
rem 移當前版本的 PyTorch 和相關
pip uninstall -y torch torchvision torchaudio
pip install virtualenv

rem 安裝最新的 PyTorch CPU 版本
pip install torch transformers opencc-python-reimplemented flask flask-cors requests


rem 這是安裝 GPU 版本的 PyTorch
rem 以下是安裝支援 CUDA 11.6 的 GPU 版本 PyTorch，根據 CUDA 版本選擇合適的版本

rem 如果您希望安裝 CUDA 版本 11.6 的 GPU 模式 PyTorch，請使用以下指令：
rem pip install torch==2.2.0+cu116 torchvision==0.15.0+cu116 torchaudio==2.2.0+cu116 -f https://download.pytorch.org/whl/torch_stable.html

rem 如果您的 GPU 支持 CUDA 11.7 或 CUDA 11.8，您可以根據 CUDA 版本進行調整：
rem CUDA 11.7 版本安裝：
rem pip install torch==2.2.0+cu117 torchvision==0.15.0+cu117 torchaudio==2.2.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html
::
rem CUDA 11.8 版本安裝：
rem pip install torch==2.2.0+cu118 torchvision==0.15.0+cu118 torchaudio==2.2.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html

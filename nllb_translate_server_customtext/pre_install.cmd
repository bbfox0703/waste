@echo off
rem 移當前版本的 PyTorch 和相關
pip uninstall -y torch torchvision torchaudio numpy transformers
pip install virtualenv

rem CPU版本
pip install -r requirements.txt

rem 如果您希望安裝 CUDA 版本的 GPU 模式 PyTorch，請使用以下指令：
rem pip uninstall torch torchvision torchaudio -y 
rem pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

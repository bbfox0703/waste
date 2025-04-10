pip install virtualenv

# 建立 CPU 環境（一次）
python -m venv cpu_env
.\cpu_env\Scripts\activate
pip install -r requirements_cpu.txt
.\cpu_env\Scripts\deactivate

# 或建立 GPU 環境（一次）
python -m venv gpu_env
.\gpu_env\Scripts\activate
.\install_gpu.cmd
pip install -r requirements_gpu.txt

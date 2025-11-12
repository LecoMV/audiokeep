#!/bin/bash
# GPU Setup Script for AudioKeep
# Run this on the GPU server to configure CUDA and models

set -e

echo "================================================"
echo "AudioKeep GPU Setup Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on GPU server
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}ERROR: nvidia-smi not found. This script must be run on a system with NVIDIA GPU.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ NVIDIA drivers detected${NC}"
nvidia-smi

echo ""
echo "================================================"
echo "System Information"
echo "================================================"

# Display GPU information
echo "GPU Information:"
nvidia-smi --query-gpu=gpu_name,memory.total,driver_version,cuda_version --format=csv,noheader

# Check CUDA version
if command -v nvcc &> /dev/null; then
    echo ""
    echo "CUDA Compiler Version:"
    nvcc --version | grep "release"
else
    echo -e "${YELLOW}WARNING: nvcc not found. CUDA toolkit may not be installed.${NC}"
fi

# Check available disk space
echo ""
echo "Disk Space:"
df -h | grep -E 'Filesystem|/$|/home'

# Check RAM
echo ""
echo "Memory:"
free -h

echo ""
echo "================================================"
echo "Python Environment Setup"
echo "================================================"

# Check Python version
if ! command -v python3.11 &> /dev/null; then
    echo -e "${YELLOW}WARNING: Python 3.11 not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-dev python3.11-venv
fi

echo -e "${GREEN}✓ Python 3.11 available${NC}"
python3.11 --version

echo ""
echo "================================================"
echo "Docker GPU Support"
echo "================================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker not found. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker installed${NC}"
docker --version

# Check NVIDIA Container Toolkit
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}WARNING: NVIDIA Container Toolkit not properly configured.${NC}"
    echo "Installing NVIDIA Container Toolkit..."

    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo systemctl restart docker

    echo -e "${GREEN}✓ NVIDIA Container Toolkit installed${NC}"
else
    echo -e "${GREEN}✓ NVIDIA Container Toolkit working${NC}"
fi

echo ""
echo "================================================"
echo "PyTorch GPU Support Test"
echo "================================================"

# Test PyTorch GPU in Docker
echo "Testing PyTorch CUDA availability in Docker..."
docker run --rm --gpus all pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PyTorch GPU support verified${NC}"
else
    echo -e "${RED}ERROR: PyTorch GPU test failed${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo "Model Cache Directory Setup"
echo "================================================"

# Create model cache directories
MODEL_DIR="/data/audiokeep/models"
UPLOAD_DIR="/data/audiokeep/uploads"
PROCESSED_DIR="/data/audiokeep/processed"

echo "Creating directories..."
sudo mkdir -p $MODEL_DIR
sudo mkdir -p $UPLOAD_DIR
sudo mkdir -p $PROCESSED_DIR

# Set permissions
sudo chown -R $USER:$USER /data/audiokeep
chmod -R 755 /data/audiokeep

echo -e "${GREEN}✓ Directories created:${NC}"
echo "  - Models: $MODEL_DIR"
echo "  - Uploads: $UPLOAD_DIR"
echo "  - Processed: $PROCESSED_DIR"

echo ""
echo "================================================"
echo "GPU Performance Settings"
echo "================================================"

# Set GPU persistence mode for better performance
echo "Enabling GPU persistence mode..."
sudo nvidia-smi -pm 1

# Set power limit if needed (optional - adjust based on your GPU)
# sudo nvidia-smi -pl 300  # Example: Set to 300W

echo -e "${GREEN}✓ GPU persistence mode enabled${NC}"

echo ""
echo "================================================"
echo "Environment Variables"
echo "================================================"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env

    # Update GPU-specific settings
    sed -i 's/TORCH_DEVICE=cpu/TORCH_DEVICE=cuda/' .env
    sed -i "s|MODEL_CACHE_DIR=/app/models|MODEL_CACHE_DIR=$MODEL_DIR|" .env
    sed -i 's/ENABLE_MIXED_PRECISION=true/ENABLE_MIXED_PRECISION=true/' .env
    sed -i 's/GPU_MEMORY_FRACTION=0.9/GPU_MEMORY_FRACTION=0.9/' .env

    echo -e "${GREEN}✓ .env file created with GPU settings${NC}"
else
    echo -e "${YELLOW}WARNING: .env file already exists. Please verify GPU settings manually.${NC}"
fi

echo ""
echo "================================================"
echo "Recommended Next Steps"
echo "================================================"
echo ""
echo "1. Download AI Models:"
echo "   python scripts/download_models.py"
echo ""
echo "2. Run GPU Benchmark:"
echo "   python scripts/benchmark_gpu.py"
echo ""
echo "3. Start Production Services:"
echo "   docker-compose up -d"
echo ""
echo "4. Monitor GPU Usage:"
echo "   watch -n 1 nvidia-smi"
echo ""
echo "5. View Logs:"
echo "   docker-compose logs -f celery-worker"
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}GPU Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"

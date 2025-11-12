# AudioKeep GPU Server Deployment Guide

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Initial Server Setup](#initial-server-setup)
4. [GPU Configuration](#gpu-configuration)
5. [AI Model Downloads](#ai-model-downloads)
6. [Docker Deployment](#docker-deployment)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

## Hardware Requirements

### Your Server Specifications
- **GPU**: NVIDIA RTX 6000 Ada (48GB VRAM) ✅
- **CPU**: AMD EPYC 9354 (32 cores, 64 threads, 3.25GHz base) ✅
- **RAM**: 87.54GB (minimum 64GB recommended) ✅
- **Storage**: 1TB+ NVMe SSD recommended

### GPU Specifications (RTX 6000 Ada)
```
Architecture: Ada Lovelace
CUDA Cores: 18,176
Tensor Cores: 568 (4th Gen)
RT Cores: 142 (3rd Gen)
Memory: 48GB GDDR6 ECC
Memory Bandwidth: 960 GB/s
TDP: 300W
Compute Capability: 8.9
```

### Performance Expectations
With this hardware, AudioKeep can process:
- **Standard Quality**: ~100 minutes of audio per minute
- **High Quality**: ~50 minutes of audio per minute
- **Ultra Quality**: ~25 minutes of audio per minute
- **Concurrent Jobs**: 8-16 simultaneous processings
- **Real-Time Factor (RTF)**: < 0.1x for most operations

## Pre-Deployment Checklist

### 1. Operating System
- [ ] Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
- [ ] Latest kernel updates installed
- [ ] SSH access configured
- [ ] Firewall configured (ports 80, 443, 8000, 5432, 6379, 9000)

### 2. NVIDIA Drivers
- [ ] NVIDIA Driver 535+ installed
- [ ] `nvidia-smi` command working
- [ ] CUDA 12.1+ installed
- [ ] cuDNN 8+ installed

### 3. Docker
- [ ] Docker 24.0+ installed
- [ ] Docker Compose 2.20+ installed
- [ ] NVIDIA Container Toolkit installed
- [ ] User added to docker group

### 4. Network
- [ ] Static IP configured
- [ ] Domain name pointed to server
- [ ] SSL certificates ready (Let's Encrypt)
- [ ] Sufficient bandwidth (100Mbps+ recommended)

### 5. Storage
- [ ] /data directory with 500GB+ free space
- [ ] Backup system configured
- [ ] NVMe SSD for model cache

## Initial Server Setup

### Step 1: System Update
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    vim \
    htop \
    iotop \
    nvtop \
    tmux \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    ffmpeg \
    libsndfile1-dev
```

### Step 2: NVIDIA Driver Installation
```bash
# Add NVIDIA repository
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update

# Install driver (check latest version)
sudo apt install -y nvidia-driver-535
sudo apt install -y nvidia-cuda-toolkit

# Reboot
sudo reboot

# Verify after reboot
nvidia-smi
nvcc --version
```

### Step 3: Docker Installation
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## GPU Configuration

### Step 4: Run GPU Setup Script
```bash
# Clone repository
git clone <your-repo-url> /opt/audiokeep
cd /opt/audiokeep

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py

# Run GPU setup script
sudo ./scripts/setup_gpu.sh
```

This script will:
- ✅ Verify GPU and drivers
- ✅ Configure GPU persistence mode
- ✅ Create model cache directories
- ✅ Set up environment variables
- ✅ Test PyTorch GPU support

### Step 5: GPU Performance Settings
```bash
# Enable persistence mode (survives reboots)
sudo nvidia-smi -pm 1

# Set power limit (optional - adjust based on cooling)
# RTX 6000 Ada default is 300W
# sudo nvidia-smi -pl 300

# Lock GPU clocks for consistent performance (optional)
# sudo nvidia-smi -lgc 2100

# Disable ECC for maximum performance (optional, reduces VRAM slightly)
# sudo nvidia-smi -e 0
```

### Step 6: Create Systemd Service for GPU Monitoring
```bash
# Create service file
sudo tee /etc/systemd/system/audiokeep-gpu-monitor.service << EOF
[Unit]
Description=AudioKeep GPU Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/audiokeep
ExecStart=/usr/bin/python3 /opt/audiokeep/scripts/monitor_gpu.py --interval 30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable audiokeep-gpu-monitor
sudo systemctl start audiokeep-gpu-monitor

# Check status
sudo systemctl status audiokeep-gpu-monitor
```

## AI Model Downloads

### Step 7: Download AI Models
```bash
cd /opt/audiokeep

# Ensure model directory exists
sudo mkdir -p /data/audiokeep/models
sudo chown -R $USER:$USER /data/audiokeep

# Run model download script
python3 scripts/download_models.py --cache-dir /data/audiokeep/models
```

Expected download sizes:
- ClearerVoice-Studio: ~500 MB
- Demucs v4: ~2 GB
- DiTSE (when available): ~3 GB
- FLowHigh (when available): ~1.5 GB
- Total: ~10-15 GB

### Step 8: Benchmark GPU Performance
```bash
# Run benchmark (this will take 5-10 minutes)
python3 scripts/benchmark_gpu.py

# Review results
cat benchmark_results.json
```

Expected RTF (Real-Time Factor) results on RTX 6000 Ada:
- Resampling: < 0.05x RTF
- Noise gate: < 0.01x RTF
- Batch processing: 4-8 files simultaneously
- Memory usage: < 20GB for typical workloads

## Docker Deployment

### Step 9: Configure Environment
```bash
cd /opt/audiokeep

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Critical .env Settings:**
```bash
# GPU Configuration
TORCH_DEVICE=cuda
ENABLE_MIXED_PRECISION=true
GPU_MEMORY_FRACTION=0.9
BATCH_INFERENCE_SIZE=4

# Model Cache
MODEL_CACHE_DIR=/data/audiokeep/models

# Database (change passwords!)
POSTGRES_PASSWORD=<strong-password-here>
POSTGRES_USER=audiokeep
POSTGRES_DB=audiokeep

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO/S3
S3_ACCESS_KEY=<random-access-key>
S3_SECRET_KEY=<strong-secret-key>

# JWT Secret (generate strong key)
JWT_SECRET_KEY=<use: openssl rand -hex 32>

# Stripe (production keys)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### Step 10: Build and Start Services
```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Step 11: Initialize Database
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create initial superuser
docker-compose exec backend python scripts/init_db.py
```

### Step 12: Verify Deployment
```bash
# Check all containers are running
docker-compose ps

# Test API
curl http://localhost:8000/health

# Test GPU in worker
docker-compose exec celery-worker python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check GPU usage
nvidia-smi
```

## Performance Optimization

### Celery Worker Configuration

Edit `docker-compose.yml`:
```yaml
celery-worker:
  # ...
  command: celery -A app.core.celery_app worker --loglevel=info --concurrency=4
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

**Concurrency Settings:**
- **RTX 6000 Ada (48GB)**: Use `--concurrency=4` to `--concurrency=8`
- Each worker uses ~6-8GB VRAM
- Monitor with `nvidia-smi` and adjust

### Database Optimization

```sql
-- Increase shared memory for PostgreSQL
-- Edit /etc/postgresql/*/main/postgresql.conf
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 64MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Redis Optimization

```bash
# Edit docker-compose.yml Redis service
redis:
  command: redis-server --maxmemory 4gb --maxmemory-policy allkeys-lru
```

## Monitoring & Maintenance

### Real-time Monitoring Dashboard

```bash
# GPU monitoring (terminal UI)
watch -n 1 nvidia-smi

# Or use nvtop
sudo apt install nvtop
nvtop

# Celery flower dashboard
# Access at http://your-server:5555
docker-compose logs -f flower

# Docker stats
docker stats

# System resources
htop
```

### Log Management

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Log rotation (configure in docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "10"
```

### Backup Strategy

```bash
# Database backup
docker-compose exec postgres pg_dump -U audiokeep audiokeep > backup_$(date +%Y%m%d).sql

# Model cache backup (optional - can re-download)
tar -czf models_backup.tar.gz /data/audiokeep/models

# Processed files (if keeping long-term)
rsync -avz /data/audiokeep/processed /backup/location/
```

### Automated Health Checks

Create `/opt/audiokeep/scripts/health_check.sh`:
```bash
#!/bin/bash
# Health check script for cron

# Check GPU
if ! nvidia-smi > /dev/null 2>&1; then
    echo "GPU check failed" | mail -s "AudioKeep Alert" admin@example.com
    exit 1
fi

# Check API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "API health check failed" | mail -s "AudioKeep Alert" admin@example.com
    exit 1
fi

# Check disk space
DISK_USAGE=$(df /data | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "Disk usage above 90%" | mail -s "AudioKeep Alert" admin@example.com
fi

exit 0
```

Add to crontab:
```bash
# Run health check every 5 minutes
*/5 * * * * /opt/audiokeep/scripts/health_check.sh
```

## Troubleshooting

### GPU Not Detected in Docker

```bash
# Check NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If fails, reinstall toolkit
sudo apt-get install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

### Out of Memory Errors

```bash
# Reduce worker concurrency
# Edit docker-compose.yml:
command: celery -A app.core.celery_app worker --concurrency=2

# Reduce batch size
# Edit .env:
BATCH_INFERENCE_SIZE=2

# Clear GPU memory
docker-compose restart celery-worker
```

### Slow Processing

```bash
# Check GPU utilization
nvidia-smi -l 1

# If < 80%, increase batch size or concurrency
# If 100%, reduce quality settings or add more GPUs

# Check CPU bottleneck
htop

# Check I/O bottleneck
iotop
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs celery-worker

# Common issues:
# - Port conflicts: Check with `netstat -tulpn`
# - Permission issues: Check with `ls -la /data/audiokeep`
# - Database connection: Check postgres logs
```

### Model Loading Failures

```bash
# Check model files exist
ls -lh /data/audiokeep/models/

# Re-download models
python3 scripts/download_models.py --cache-dir /data/audiokeep/models

# Check disk space
df -h /data

# Check permissions
sudo chown -R 1000:1000 /data/audiokeep/models
```

## Production Deployment Checklist

Before going live:

### Security
- [ ] Change all default passwords
- [ ] Generate strong JWT secrets
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable fail2ban
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts

### Performance
- [ ] Run GPU benchmark
- [ ] Optimize worker concurrency
- [ ] Configure database connection pool
- [ ] Set up Redis persistence
- [ ] Enable Nginx caching
- [ ] Configure CDN for static assets

### Monitoring
- [ ] Set up Prometheus + Grafana
- [ ] Configure alert rules
- [ ] Set up log aggregation
- [ ] Enable error tracking (Sentry)
- [ ] Configure uptime monitoring

### Documentation
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures
- [ ] Create disaster recovery plan

## Maintenance Schedule

### Daily
- Check GPU health monitor logs
- Review error logs
- Monitor disk space

### Weekly
- Review performance metrics
- Check for security updates
- Verify backups are running

### Monthly
- Update Docker images
- Review and rotate logs
- Performance optimization review
- Security audit

## Support

For issues or questions:
- Documentation: `/opt/audiokeep/docs/`
- Logs: `/var/log/audiokeep/`
- GPU Metrics: `/var/log/audiokeep/gpu_metrics.jsonl`
- Health Status: `http://your-server:8000/health`

---

**Deployment Guide Version**: 1.0
**Last Updated**: November 2025
**Target Hardware**: RTX 6000 Ada / AMD EPYC 9354

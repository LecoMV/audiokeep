# AudioKeep - Professional AI Audio Restoration Platform

AudioKeep is a world-class AI-powered audio restoration and enhancement platform designed for professionals in archival preservation, audio forensics, broadcast restoration, and historical audio digitization.

## Features

### Audio Restoration
- Advanced noise reduction (background noise, hiss, hum, buzz)
- Click and pop removal (vinyl/tape damage)
- Spectral repair for damaged audio sections
- Declipping for distorted audio restoration
- Electrical interference removal (50/60Hz hum)

### Audio Enhancement
- AI-powered speech enhancement
- Audio super-resolution (upsample to 48kHz/96kHz/192kHz)
- Voice isolation and source separation
- Bandwidth extension
- Dynamic range enhancement

### Professional Features
- Audio forensics tools for law enforcement
- Detailed spectral analysis
- Authentication and tampering detection
- Forensic reporting
- Batch processing capabilities

### User Features
- Real-time A/B comparison player
- Waveform and spectrogram visualization
- Credit-based pricing model
- Multiple quality tiers
- API access for enterprise

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PyTorch** - AI model inference
- **Celery** - Distributed task queue
- **PostgreSQL** - Primary database
- **Redis** - Queue and caching
- **MinIO/S3** - File storage

### Frontend
- **React 18+** with TypeScript
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Shadcn/ui** - Component library
- **React Query** - Data fetching
- **Zustand** - State management
- **Wavesurfer.js** - Audio visualization

### AI Models
- **Resemble Enhance** - Speech denoising and enhancement
- **AudioSR** - Audio super-resolution
- **DeepFilterNet** - Advanced noise reduction
- **Demucs v4** - Source separation
- **FlashSR** - Fast super-resolution

## Hardware Requirements

### Development
- 8GB+ RAM
- 4+ CPU cores
- 10GB disk space

### Production (Recommended)
- **GPU**: NVIDIA RTX 6000 Ada (48GB VRAM)
- **CPU**: AMD EPYC 9354 (32 cores, 64 threads)
- **RAM**: 128GB
- **Storage**: 1TB NVMe SSD

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- NVIDIA GPU with CUDA 12.x (for production)

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/audiokeep.git
cd audiokeep
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start development environment**
```bash
docker-compose -f docker-compose.dev.yml up
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production deployment instructions.

## Project Structure

```
audiokeep/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API route handlers
│   │   ├── core/                # Core configuration
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── ai_models/           # AI model integrations
│   │   └── db/                  # Database utilities
│   ├── tests/                   # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API services
│   │   ├── store/               # State management
│   │   └── types/               # TypeScript types
│   ├── public/                  # Static assets
│   └── package.json
├── deployment/
│   ├── docker/                  # Dockerfiles
│   └── kubernetes/              # K8s manifests
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── ARCHITECTURE.md              # System architecture
└── docker-compose.yml
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## Credit System

AudioKeep uses a credit-based pricing model:

### Free Tier
- 50 credits on signup
- Standard quality processing
- Max 100MB file size
- Max 30 minutes duration

### Credit Packs
- **Starter**: 100 credits - $9.99
- **Professional**: 500 credits - $39.99
- **Studio**: 1,500 credits - $99.99
- **Enterprise**: 5,000 credits - $299.99

### Monthly Subscriptions
- **Pro**: $29.99/month (500 credits)
- **Studio**: $79.99/month (1,500 credits)
- **Forensic**: $199.99/month (4,000 credits + forensic tools)

### Credit Usage Examples
- 1-minute podcast cleanup: ~2 credits
- 10-minute interview restoration: ~35 credits
- 60-minute archival tape (ultra quality): ~240 credits
- 5-minute forensic analysis: ~30 credits

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

Copyright (c) 2025 AudioKeep. All rights reserved.

This is proprietary software. See [LICENSE.md](LICENSE.md) for details.

## Support

- Documentation: https://docs.audiokeep.io
- Email: support@audiokeep.io
- Issue Tracker: https://github.com/yourusername/audiokeep/issues

## Roadmap

### Phase 1 (Q1 2025) - MVP
- Core audio processing features
- User authentication and credits system
- Basic UI with upload/download
- Stripe payment integration

### Phase 2 (Q2 2025) - Enhancement
- Subscription tiers
- Batch processing
- Advanced visualizations
- Email notifications

### Phase 3 (Q3 2025) - Professional
- Forensic analysis tools
- API for enterprise
- Team accounts
- Priority processing queue

### Phase 4 (Q4 2025) - Scale
- Mobile applications
- DAW plugin integrations
- White-label solutions
- Advanced analytics

## Authors

AudioKeep Development Team

## Acknowledgments

- Resemble AI for Resemble Enhance
- Meta/Facebook Research for Demucs
- Open-source audio processing community
- All contributors and testers

---

**Built with ❤️ for audio preservation professionals worldwide**

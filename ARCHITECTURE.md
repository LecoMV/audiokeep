# AudioKeep - Architecture Documentation

## Overview
AudioKeep is a world-class AI-powered audio restoration and enhancement platform designed for professional use cases including archival preservation, audio forensics, broadcast restoration, and historical audio digitization.

## Target Market

### Primary Users
- Museums, libraries, and historical societies
- Audio forensics professionals and law enforcement
- Film/video production companies
- Academic researchers (oral history, linguistics)
- Legal professionals (court recordings, depositions)
- Broadcasting companies (archive restoration)
- Insurance companies (claims investigation)

### Secondary Users
- Podcasters and content creators
- Genealogy researchers
- Musicians (restoration of vintage recordings)

## Core Features

### 1. Audio Restoration
- **Noise Reduction**: Remove background noise, hiss, hum, buzz
- **Click/Pop Removal**: Eliminate clicks from vinyl/tape damage
- **Spectral Repair**: Fix dropouts and damaged audio sections
- **Declipping**: Restore clipped/distorted audio
- **Dehum/Debuzz**: Remove electrical interference (50/60Hz)

### 2. Audio Enhancement
- **Speech Enhancement**: Clarity improvement for voice recordings
- **Audio Super-Resolution**: Upsample to 48kHz/96kHz/192kHz
- **Voice Isolation**: Separate speech from background
- **Bandwidth Extension**: Restore lost frequencies
- **Dynamic Range Enhancement**: Improve overall audio quality

### 3. Audio Forensics (Professional Tier)
- **Voice Enhancement**: Law enforcement evidence processing
- **Spectral Analysis**: Detailed frequency visualization
- **Authentication Analysis**: Detect tampering/edits
- **Source Separation**: Isolate individual audio sources
- **Forensic Reporting**: Generate detailed analysis reports

### 4. Batch Processing
- Process multiple files simultaneously
- Queue management
- Progress tracking
- Bulk download

### 5. Quality Control
- A/B comparison player (before/after)
- Waveform visualization
- Spectrogram analysis
- Quality metrics and measurements

## AI Models Stack

### Primary Models
1. **Resemble Enhance** (Open Source)
   - Speech denoising and enhancement
   - Two-stage processing: denoiser + enhancer
   - Excellent for voice restoration

2. **AudioSR** (Open Source)
   - Versatile audio super-resolution
   - Upsampling to 48kHz
   - Handles speech, music, and sound effects

3. **DeepFilterNet** (Open Source)
   - Advanced speech enhancement
   - Harmonic structure preservation
   - Low-latency processing

4. **Demucs v4** (Meta/Facebook Research)
   - Source separation (vocals, drums, bass, other)
   - Hybrid Transformer architecture
   - Useful for isolating speech from music

5. **FlashSR** (Research)
   - Single-step diffusion model
   - 22x faster than traditional methods
   - 48kHz output

### GPU Acceleration
- **NVIDIA RTX 6000 Ada**: 48GB VRAM, 18,176 CUDA cores
- **PyTorch with CUDA 12.x**
- Batch processing optimization
- Mixed precision (FP16/FP32) for speed

## Technical Architecture

### Backend Stack
```
FastAPI (Python 3.11+)
├── API Layer (REST + WebSocket)
├── Authentication (JWT)
├── File Upload/Management
├── Job Queue (Celery + Redis)
├── AI Processing Pipeline
└── Database (PostgreSQL)
```

### Frontend Stack
```
React 18+ with TypeScript
├── Vite (Build Tool)
├── TailwindCSS (Styling)
├── Shadcn/ui (Components)
├── Zustand (State Management)
├── React Query (Data Fetching)
├── Wavesurfer.js (Audio Visualization)
└── React Dropzone (File Upload)
```

### Infrastructure
```
Docker Compose
├── FastAPI Backend
├── PostgreSQL Database
├── Redis (Queue + Cache)
├── Celery Worker (AI Processing)
├── Nginx (Reverse Proxy)
└── MinIO/S3 (File Storage)
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        React Frontend                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  Upload  │  │ Process  │  │ Compare  │  │  Download   │ │
│  │  Files   │  │ Settings │  │  Audio   │  │   Results   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                        HTTPS/WSS
                              │
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │   Auth   │  │  Upload  │  │  Jobs    │  │   Credits   │ │
│  │  Service │  │  Service │  │  Service │  │   Service   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                │                │
    ┌────┴────┐      ┌────┴────┐     ┌────┴────┐
    │PostgreSQL│      │  Redis  │     │  MinIO  │
    │ Database │      │  Queue  │     │  S3     │
    └──────────┘      └─────────┘     └─────────┘
                           │
                           │
┌──────────────────────────────────────────────────────────────┐
│                    Celery Worker Pool                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              AI Processing Pipeline                     │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │  │
│  │  │ Resemble│  │AudioSR  │  │DeepFilter│  │  Demucs  │  │  │
│  │  │ Enhance │  │         │  │   Net    │  │          │  │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └──────────┘  │  │
│  │                                                          │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │        PyTorch + CUDA (RTX 6000 Ada)            │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Credit System Design

### Credit Calculation Formula
```python
base_cost = file_duration_seconds / 60  # Base: 1 credit per minute

# Multipliers
quality_multiplier = {
    'standard': 1.0,    # 48kHz, basic processing
    'high': 2.0,        # 96kHz, advanced processing
    'ultra': 4.0,       # 192kHz, maximum quality
    'forensic': 6.0     # Forensic analysis + reporting
}

# Feature multipliers (additive)
features_multiplier = 1.0
if noise_reduction: features_multiplier += 0.3
if speech_enhancement: features_multiplier += 0.4
if super_resolution: features_multiplier += 0.5
if source_separation: features_multiplier += 0.8
if spectral_repair: features_multiplier += 0.6
if forensic_analysis: features_multiplier += 1.5

total_credits = base_cost * quality_multiplier * features_multiplier
```

### Pricing Tiers

#### Free Tier
- **50 credits** on signup
- Standard quality only
- Basic features (noise reduction, basic enhancement)
- Watermark on exports (optional)
- Max file size: 100MB
- Max duration: 30 minutes

#### Credit Packs (One-time Purchase)
- **Starter**: 100 credits - $9.99 ($0.10/credit)
- **Professional**: 500 credits - $39.99 ($0.08/credit)
- **Studio**: 1,500 credits - $99.99 ($0.067/credit)
- **Enterprise**: 5,000 credits - $299.99 ($0.06/credit)
- Credits never expire
- All quality levels unlocked
- No watermark
- Max file size: 500MB
- Max duration: 2 hours

#### Monthly Subscriptions (Best Value)
- **Pro**: $29.99/month
  - 500 credits/month ($0.06/credit)
  - Rollover: 100 credits/month
  - High quality unlocked
  - Priority processing
  - Max file size: 1GB
  - Max duration: 4 hours

- **Studio**: $79.99/month
  - 1,500 credits/month ($0.053/credit)
  - Rollover: 300 credits/month
  - Ultra quality unlocked
  - Highest priority processing
  - Max file size: 2GB
  - Max duration: 8 hours

- **Forensic**: $199.99/month
  - 4,000 credits/month ($0.05/credit)
  - Rollover: 500 credits/month
  - All features including forensic analysis
  - Dedicated support
  - API access
  - Unlimited file size/duration
  - Forensic reporting

### Credit Usage Examples
- **1-minute podcast cleanup** (noise reduction + enhancement): ~2 credits
- **10-minute interview restoration** (high quality, all features): ~35 credits
- **60-minute archival tape** (ultra quality, full restoration): ~240 credits
- **5-minute forensic analysis** (complete analysis + report): ~30 credits

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    email_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50),
    stripe_customer_id VARCHAR(255),
    last_login TIMESTAMP
);
```

### Credits Table
```sql
CREATE TABLE credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'purchase', 'subscription', 'bonus', 'refund'
    transaction_date TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    stripe_payment_id VARCHAR(255)
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    original_filename VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    duration_seconds DECIMAL(10,2),
    status VARCHAR(50) NOT NULL, -- 'queued', 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    credits_used DECIMAL(10,2),
    settings JSONB NOT NULL,
    error_message TEXT,
    input_file_url VARCHAR(1000),
    output_file_url VARCHAR(1000),
    quality_metrics JSONB
);
```

### Subscriptions Table
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    tier VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/verify-email` - Verify email
- `POST /api/v1/auth/reset-password` - Password reset

### User Management
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile
- `GET /api/v1/users/me/credits` - Get credit balance
- `GET /api/v1/users/me/usage` - Get usage statistics

### Credits & Payments
- `POST /api/v1/credits/purchase` - Purchase credit pack
- `POST /api/v1/subscriptions/create` - Create subscription
- `POST /api/v1/subscriptions/cancel` - Cancel subscription
- `GET /api/v1/credits/history` - Credit transaction history

### Audio Processing
- `POST /api/v1/jobs/upload` - Upload audio file
- `POST /api/v1/jobs/{job_id}/process` - Start processing
- `GET /api/v1/jobs/{job_id}` - Get job status
- `GET /api/v1/jobs/{job_id}/download` - Download result
- `GET /api/v1/jobs` - List user's jobs
- `DELETE /api/v1/jobs/{job_id}` - Delete job
- `POST /api/v1/jobs/batch` - Batch upload
- `WS /api/v1/jobs/{job_id}/progress` - Real-time progress updates

### Analysis
- `GET /api/v1/jobs/{job_id}/analysis` - Get audio analysis
- `GET /api/v1/jobs/{job_id}/spectrogram` - Get spectrogram image
- `GET /api/v1/jobs/{job_id}/waveform` - Get waveform data

## Processing Pipeline

### 1. File Upload
```python
1. Client uploads file via multipart/form-data
2. Validate file format (WAV, MP3, FLAC, M4A, OGG, etc.)
3. Validate file size and duration
4. Calculate estimated credit cost
5. Check user credit balance
6. Upload to S3/MinIO
7. Create job record in database
8. Return job_id to client
```

### 2. Processing Queue
```python
1. Job added to Celery queue
2. Worker picks up job
3. Download file from S3
4. Extract audio metadata
5. Convert to standard format (WAV 16-bit)
6. Load audio into PyTorch tensor
7. Move to GPU
```

### 3. AI Processing Chain
```python
# Stage 1: Noise Reduction
if settings.noise_reduction:
    audio = deepfilternet.process(audio)

# Stage 2: Speech Enhancement
if settings.speech_enhancement:
    audio = resemble_enhance.enhance(audio)

# Stage 3: Source Separation (if needed)
if settings.voice_isolation:
    vocals = demucs.separate(audio, stem='vocals')
    audio = vocals

# Stage 4: Spectral Repair
if settings.spectral_repair:
    audio = spectral_repair.process(audio)

# Stage 5: Super Resolution
if settings.target_sample_rate > original_sample_rate:
    audio = audiosr.upsample(audio, target_rate=settings.target_sample_rate)

# Stage 6: Final Enhancement
audio = final_mastering.process(audio)
```

### 4. Quality Analysis
```python
# Calculate metrics
snr = calculate_snr(audio)
thd = calculate_thd(audio)
dynamic_range = calculate_dynamic_range(audio)
spectral_centroid = calculate_spectral_centroid(audio)

# Store metrics
quality_metrics = {
    'snr_db': snr,
    'thd_percent': thd,
    'dynamic_range_db': dynamic_range,
    'spectral_centroid_hz': spectral_centroid
}
```

### 5. Export & Delivery
```python
1. Export to requested format (WAV, FLAC, MP3)
2. Upload to S3
3. Generate download URL (signed, 7-day expiration)
4. Update job status to 'completed'
5. Deduct credits from user account
6. Send WebSocket notification to client
7. Send email notification (optional)
```

## User Workflow

### New User Journey
1. Land on homepage → See demo/examples
2. Sign up (email/Google OAuth)
3. Receive 50 free credits
4. Tutorial overlay guides first upload
5. Upload test file (< 5 min recommended)
6. Select processing options
7. See credit cost estimate
8. Click "Process"
9. Real-time progress updates
10. A/B comparison player
11. Download result
12. Prompt to purchase credits or subscribe

### Returning User Journey
1. Login → Dashboard
2. See credit balance prominently
3. Recent jobs displayed
4. Quick upload or batch upload
5. Saved presets for common workflows
6. One-click re-process with different settings
7. Manage subscriptions/credits

## UI/UX Design Principles

### Visual Design
- Clean, professional interface
- Dark mode optimized for audio work
- Waveform and spectrogram visualizations
- Real-time processing feedback
- Minimal clicks to complete tasks

### Key Pages

#### 1. Homepage
- Hero with demo player (before/after audio)
- Use case showcases (forensics, archival, etc.)
- Pricing comparison table
- Customer testimonials
- Technical capabilities section

#### 2. Dashboard
- Credit balance (prominent)
- Recent jobs (with thumbnails)
- Quick upload area
- Usage statistics chart
- Subscription status

#### 3. Upload & Process
- Drag-and-drop file upload
- Multi-file selection
- Processing options (expandable sections)
- Real-time credit cost calculator
- Quality preset selector
- Advanced options (collapsible)

#### 4. Results Page
- Split view: original vs. processed
- Synchronized playback
- Waveform visualization
- Spectrogram comparison
- Quality metrics display
- Download options (format selection)
- Re-process with different settings

#### 5. Settings
- Profile management
- Subscription management
- Credit history
- API keys (for enterprise)
- Notification preferences
- Saved presets

## Performance Targets

### Processing Speed
- Real-time factor (RTF) targets:
  - Noise reduction: < 0.1x (10 min audio in 1 min)
  - Speech enhancement: < 0.2x
  - Super resolution: < 0.5x
  - Full pipeline: < 1.0x (10 min audio in 10 min)

### API Response Times
- File upload: < 2s for 100MB
- Job submission: < 500ms
- Status check: < 100ms
- Credit balance: < 50ms

### Scalability
- Support 100 concurrent users initially
- Horizontal scaling for Celery workers
- Auto-scaling based on queue depth
- Target: 1000+ concurrent users

## Security Considerations

### Authentication & Authorization
- JWT with refresh tokens
- Password hashing (bcrypt, 12 rounds)
- Rate limiting on all endpoints
- Email verification required
- OAuth2 for Google/GitHub login

### File Security
- Virus scanning on upload
- File type validation (magic bytes)
- Size limits per tier
- Automatic deletion after 30 days
- Encrypted S3 storage

### Payment Security
- Stripe integration (PCI compliant)
- No credit card storage
- Webhook signature verification
- Idempotency keys for charges

### Data Privacy
- GDPR compliant
- User data deletion on request
- Audio files encrypted at rest
- No AI model training on user data
- Clear privacy policy

## Monitoring & Analytics

### Application Monitoring
- Error tracking (Sentry)
- Performance monitoring (APM)
- Database query optimization
- GPU utilization monitoring
- Queue depth and worker health

### Business Metrics
- Daily/Monthly Active Users (DAU/MAU)
- Credit consumption rate
- Conversion rate (free → paid)
- Subscription retention rate
- Average revenue per user (ARPU)
- Processing job success rate

### User Analytics
- Feature usage patterns
- Most common quality settings
- File format preferences
- A/B test results
- User feedback and satisfaction

## Deployment Strategy

### Development Environment
- Docker Compose for local development
- Hot reload for backend and frontend
- Mock S3 (MinIO)
- Mock payment gateway (Stripe test mode)

### Staging Environment
- Kubernetes cluster
- Automated CI/CD (GitHub Actions)
- Database migrations (Alembic)
- Integration tests
- Load testing

### Production Environment
- Multi-region deployment (US, EU)
- CDN for static assets (CloudFront)
- Database replication
- Automated backups
- Blue-green deployments
- Rollback capability

## Roadmap

### Phase 1: MVP (Months 1-3)
- Core audio processing (noise reduction, enhancement)
- User authentication and credits system
- Basic UI with upload/download
- Standard quality processing
- Stripe integration (credit packs)

### Phase 2: Enhancement (Months 4-6)
- Subscription tiers
- High/Ultra quality processing
- Batch processing
- Advanced visualizations
- A/B comparison player
- Email notifications

### Phase 3: Professional Features (Months 7-9)
- Forensic analysis tools
- Spectral repair
- API for enterprise customers
- Advanced reporting
- Team accounts
- Priority queue

### Phase 4: Scale & Optimize (Months 10-12)
- Mobile apps (iOS/Android)
- Plugin integrations (DAWs)
- Custom model training (enterprise)
- White-label solution
- Advanced analytics dashboard

## Competitive Advantages

1. **Web-based**: No software installation required
2. **Credit System**: Pay only for what you use
3. **Professional Grade**: Matches desktop software quality
4. **GPU Accelerated**: Fast processing times
5. **Multiple AI Models**: Best-in-class results
6. **User Friendly**: Intuitive interface
7. **Forensic Features**: Specialized tools for professionals
8. **Transparent Pricing**: Clear credit costs upfront
9. **API Access**: Automation for enterprise
10. **Continuous Updates**: Regular model improvements

## Success Metrics

### Year 1 Goals
- 10,000+ registered users
- 1,000+ paid customers
- $50,000+ MRR (Monthly Recurring Revenue)
- 95%+ job success rate
- < 2% churn rate
- 4.5+ star rating

### Technical Goals
- 99.9% uptime SLA
- < 100ms average API response time
- < 0.5x average RTF for processing
- Zero data breaches
- < 1% error rate

## Integration with PhotoKeep Ecosystem

### Shared Features
- Unified user accounts (SSO)
- Combined credit system (optional)
- Shared cloud storage
- Consistent UI/UX design
- Cross-product promotions

### Bundle Opportunities
- "Multimedia Restoration Suite"
- Combined subscriptions at discount
- Shared enterprise plans
- Unified API

## Conclusion

AudioKeep is positioned to become the industry-leading web-based audio restoration platform by combining cutting-edge AI technology, professional-grade features, and user-friendly design with a flexible credit-based pricing model that serves everyone from individual researchers to large institutions.

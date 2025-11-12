# AudioKeep - State-of-the-Art AI Models (November 2025)

## Executive Summary

This document outlines the most powerful audio AI models available as of November 2025 for integration into AudioKeep. Our research has identified cutting-edge models that significantly outperform earlier generations in audio restoration, enhancement, and super-resolution.

## Latest Breakthrough Models (2025)

### 1. Speech Enhancement

#### DiTSE - Diffusion Transformer for Speech Enhancement ⭐ **RECOMMENDED**
- **Release**: 2025
- **Technology**: Diffusion Transformer (DiT) on VAE latent representations
- **Performance**: First model to match real studio quality from DAPS benchmark
- **Key Features**:
  - Full-bandwidth (48kHz) restoration
  - Superior speaker preservation
  - Reduced content hallucination
  - Transformer-based backbone (more scalable than U-Net)
- **Advantages**: State-of-the-art audio quality, excellent for professional archival work
- **GitHub**: Research paper available on arXiv
- **Integration Priority**: **HIGH** - This is the best available model for speech enhancement

#### Diffusion Buffer for Online Enhancement
- **Release**: October 2025
- **Technology**: Online generative diffusion-based enhancement
- **Performance**: 32-176ms latency (down from 320-960ms)
- **Key Features**:
  - Real-time processing capability
  - Single neural network call per frame
  - Consumer-grade GPU compatible
  - Stream processing support
- **Advantages**: Ultra-low latency for real-time applications
- **Use Case**: Real-time preview, live processing features

### 2. Audio Super-Resolution

#### FLowHigh ⭐ **RECOMMENDED**
- **Release**: January 2025
- **Technology**: Flow matching for audio super-resolution
- **Performance**: State-of-the-art on VCTK benchmark
- **Key Features**:
  - Single-step sampling (extremely fast)
  - High-fidelity output
  - Works across various input sampling rates
  - Computationally efficient
- **Advantages**: Best balance of quality and speed
- **Integration Priority**: **HIGH** - Replace AudioSR with this

#### Audio Super-Resolution with Latent Bridge Models (LBMs)
- **Release**: September 2025
- **Technology**: Latent-to-latent generation
- **Performance**: First model achieving any-to-192kHz upsampling
- **Key Features**:
  - Upsampling to 48kHz, 96kHz, and 192kHz
  - Works on speech, audio, and music
  - Continuous latent space compression
- **Advantages**: Highest quality super-resolution available
- **Integration Priority**: **HIGH** - For ultra-quality tier

#### ClearerVoice-Studio
- **Release**: June 2025
- **Technology**: Open-source AI toolkit
- **Performance**: State-of-the-art pretrained models
- **Key Features**:
  - Speech enhancement
  - Speech separation
  - Super-resolution
  - Multimodal target speaker extraction
  - FRCRN model (3M uses)
  - MossFormer model (2.5M uses)
- **Advantages**: Comprehensive toolkit, proven in production
- **Integration Priority**: **MEDIUM-HIGH**

### 3. Transcription & Speech Recognition

#### OpenAI GPT-4o Transcribe
- **Release**: March 2025
- **Technology**: GPT-4o-based transcription
- **Performance**: Lower WER than Whisper
- **Key Features**:
  - Better accent recognition
  - Improved noisy environment handling
  - Better with varying speech speeds
  - Enhanced language recognition
- **Models**:
  - `gpt-4o-transcribe` (highest quality)
  - `gpt-4o-mini-transcribe` (faster, cost-effective)
- **Advantages**: Industry-leading transcription accuracy
- **Use Case**: Forensic analysis, transcription features

#### NVIDIA Riva 2.19.0
- **Release**: March 2025
- **Technology**: GPU-accelerated multilingual speech AI
- **Models**:
  - **Canary-Qwen-2.5B** (Top Hugging Face leaderboard)
  - **Magpie TTS** (Multilingual, zero-shot, flow-based)
- **Key Features**:
  - Real-time ASR, TTS, NMT
  - GPU-optimized for RTX series
  - Multilingual support
  - Customizable for specific domains
- **Advantages**: Perfect for our RTX 6000 Ada GPU
- **Integration Priority**: **MEDIUM** - Consider for ASR features

### 4. Alternatives & Competitors

#### Voxtral (Mistral AI)
- **Release**: 2025
- **Description**: "New standard" Whisper alternative
- **Technology**: Open-source speech recognition
- **Performance**: Competitive with Whisper-large-v3

#### Drax (aiOla)
- **Release**: 2025
- **Performance**: WER 7.4% (on par with Whisper-large-v3 at 7.6%)
- **Speed**: Up to 5x faster than Whisper
- **Advantages**: Best speed-to-accuracy ratio

## Commercial State-of-the-Art (2025)

### iZotope RX 11
- **Status**: Industry gold standard
- **Technology**: Proprietary ML + spectral analysis
- **Features**: Comprehensive restoration suite
- **Price**: $400-$1,200
- **Note**: We aim to match or exceed this quality

### Accentize dxRevive
- **Status**: Leading dialogue restoration
- **Technology**: ML trained on professional recordings
- **Features**: One-click restoration
- **Price**: ~$300

### Waves Clarity Vx Pro
- **Status**: Real-time vocal cleanup
- **Technology**: Dual AI models (Broad 1 & 2)
- **Features**: Real-time neural processing
- **Price**: ~$400

## Recommended Model Stack for AudioKeep

### Tier 1: Core Models (Implement First)

1. **Speech Enhancement**: DiTSE
   - Best overall quality
   - Professional archival standard
   - Studio-quality output

2. **Super-Resolution**: FLowHigh
   - Fastest single-step processing
   - Excellent quality
   - Energy efficient

3. **Noise Reduction**: ClearerVoice-Studio (FRCRN)
   - Proven in production (3M uses)
   - Open-source
   - Excellent documentation

### Tier 2: Advanced Features

4. **Real-time Enhancement**: Diffusion Buffer
   - For live preview features
   - Low-latency processing
   - Phase 2 implementation

5. **Ultra Quality SR**: Latent Bridge Models
   - For forensic/ultra tier
   - 192kHz capability
   - Phase 2 implementation

6. **Transcription**: GPT-4o-transcribe
   - For forensic reports
   - Metadata generation
   - Phase 3 implementation

### Tier 3: Specialized Tools

7. **Source Separation**: Demucs v4 (Meta)
   - Voice isolation
   - Hybrid Transformer
   - Already planned

8. **GPU Optimization**: NVIDIA Riva
   - For real-time features
   - Multi-language support
   - Phase 3 consideration

## Performance Comparison Matrix

| Model | Quality | Speed | GPU Memory | Use Case |
|-------|---------|-------|------------|----------|
| DiTSE | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | High | Speech Enhancement |
| FLowHigh | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium | Super-Resolution |
| LBMs | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | High | Ultra SR (192kHz) |
| ClearerVoice | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Medium | Noise Reduction |
| Diffusion Buffer | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low | Real-time |
| GPT-4o-transcribe | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Low | ASR |
| Demucs v4 | ⭐⭐⭐⭐ | ⭐⭐⭐ | Medium | Separation |

## Implementation Roadmap

### Phase 1 (Immediate - Next 2 Weeks)

1. **Integrate DiTSE**
   - Download and test model
   - Create PyTorch inference wrapper
   - Benchmark on RTX 6000 Ada
   - Target: < 0.2x RTF

2. **Integrate FLowHigh**
   - Replace current AudioSR placeholder
   - Test 48kHz → 96kHz upsampling
   - Benchmark performance
   - Target: < 0.1x RTF

3. **Deploy ClearerVoice-Studio FRCRN**
   - Set up model pipeline
   - Create noise reduction service
   - Integration testing
   - Target: < 0.1x RTF

### Phase 2 (Month 2)

4. **Add Diffusion Buffer**
   - Real-time preview feature
   - WebSocket integration
   - Low-latency optimization

5. **Integrate LBMs**
   - Ultra quality tier (192kHz)
   - Forensic processing
   - Extended processing time acceptable

### Phase 3 (Month 3)

6. **Add GPT-4o Transcribe**
   - OpenAI API integration
   - Forensic report generation
   - Metadata extraction

7. **Optimize with NVIDIA Riva**
   - Evaluate for specific features
   - Multi-language support
   - Real-time ASR if needed

## Technical Requirements

### GPU Requirements (RTX 6000 Ada)
- **VRAM**: 48GB (sufficient for all models)
- **CUDA**: 12.1+ recommended
- **Compute Capability**: 8.9 (Ada Lovelace)
- **Memory Bandwidth**: 960 GB/s

### Software Stack
```python
torch >= 2.2.0
torchaudio >= 2.2.0
transformers >= 4.37.0
diffusers >= 0.26.0
accelerate >= 0.26.0
```

### Model Storage Requirements
- DiTSE: ~2-4 GB
- FLowHigh: ~1-2 GB
- ClearerVoice-Studio: ~500 MB
- Latent Bridge Models: ~3-5 GB
- **Total**: ~10-15 GB for all models

## Licensing Considerations

### Open Source Models
- **DiTSE**: Research/Apache 2.0 (verify)
- **FLowHigh**: Research/MIT (verify)
- **ClearerVoice-Studio**: MIT License ✓
- **Demucs**: MIT License ✓

### Commercial APIs
- **GPT-4o Transcribe**: OpenAI API (pay-per-use)
- **NVIDIA Riva**: Free for development, enterprise licensing

### Action Required
- Verify licensing for DiTSE and FLowHigh
- Review commercial use terms
- Consider hybrid approach (open + API)

## Competitive Advantages

By implementing these models, AudioKeep will:

1. ✅ **Match iZotope RX quality** (DiTSE = studio quality)
2. ✅ **Exceed Waves Clarity Vx speed** (FLowHigh single-step)
3. ✅ **Surpass Adobe Podcast features** (more control, better quality)
4. ✅ **Offer unique 192kHz capability** (LBMs - no competitor has this)
5. ✅ **Provide real-time preview** (Diffusion Buffer - unique feature)
6. ✅ **Enable forensic-grade transcription** (GPT-4o - investigator needs)

## Risk Mitigation

### Model Availability
- **Fallback Strategy**: Keep current implementations as backup
- **Gradual Rollout**: A/B test new models
- **Version Control**: Maintain multiple model versions

### Performance Issues
- **Monitoring**: Track RTF per model
- **Auto-scaling**: Add workers if queue grows
- **Caching**: Cache model weights in GPU memory

### Quality Assurance
- **Automated Testing**: PESQ, STOI metrics
- **Human Evaluation**: A/B listening tests
- **Customer Feedback**: Rating system per job

## Next Steps

### Week 1-2: Research & Setup
- [ ] Download DiTSE model weights
- [ ] Download FLowHigh model weights
- [ ] Install ClearerVoice-Studio
- [ ] Create benchmark suite
- [ ] Test on sample audio files

### Week 3-4: Integration
- [ ] Implement DiTSE inference pipeline
- [ ] Implement FLowHigh SR pipeline
- [ ] Replace model placeholders
- [ ] Update API to expose new features
- [ ] Documentation updates

### Week 5-6: Testing & Optimization
- [ ] GPU memory optimization
- [ ] Batch processing tests
- [ ] A/B quality comparisons
- [ ] Performance benchmarking
- [ ] User acceptance testing

### Week 7-8: Production Deployment
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor performance metrics
- [ ] Collect user feedback
- [ ] Fine-tune parameters
- [ ] Full production release

## References

### Research Papers
- DiTSE: "High-Fidelity Generative Speech Enhancement via Latent Diffusion Transformers" (2025)
- FLowHigh: "Towards Efficient and High-Quality Audio SR with Single-Step Flow Matching" (Jan 2025)
- LBMs: "Audio Super-Resolution with Latent Bridge Models" (Sep 2025)
- Diffusion Buffer: "Diffusion Buffer for Online Generative Speech Enhancement" (Oct 2025)

### GitHub Repositories
- ClearerVoice-Studio: https://github.com/modelscope/ClearerVoice-Studio
- Demucs: https://github.com/facebookresearch/demucs
- AudioCraft: https://github.com/facebookresearch/audiocraft

### Commercial Tools
- iZotope RX 11: https://www.izotope.com/en/products/rx.html
- Waves Clarity Vx: https://www.waves.com/plugins/clarity-vx
- NVIDIA Riva: https://developer.nvidia.com/riva

---

**Last Updated**: November 2025
**Status**: Research Complete, Ready for Implementation
**Priority**: HIGH - These models give AudioKeep industry-leading capabilities

"""
AI Model Manager
Loads and manages audio processing AI models
"""
import torch
import torchaudio
import numpy as np
import logging
from typing import Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages AI models for audio processing

    Lazy-loads models only when needed to conserve memory
    """

    def __init__(self):
        self.device = torch.device(settings.TORCH_DEVICE)
        self.models = {}

        # Model cache directory
        self.cache_dir = Path(settings.MODEL_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ModelManager initialized on device: {self.device}")

    async def apply_noise_reduction(
        self,
        waveform: torch.Tensor,
        sample_rate: int,
        strength: float = 0.5
    ) -> torch.Tensor:
        """
        Apply noise reduction using DeepFilterNet

        NOTE: This is a simplified version. In production, implement full DeepFilterNet integration.
        """
        try:
            # For now, apply a simple noise gate as placeholder
            # In production, use DeepFilterNet or similar model
            threshold = 0.01 * (1.0 - strength)
            mask = torch.abs(waveform) > threshold
            denoised = waveform * mask.float()

            logger.info(f"Applied noise reduction with strength {strength}")
            return denoised

        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            return waveform

    async def apply_speech_enhancement(
        self,
        waveform: torch.Tensor,
        sample_rate: int
    ) -> torch.Tensor:
        """
        Apply speech enhancement using Resemble Enhance

        NOTE: Placeholder implementation. Integrate Resemble Enhance in production.
        """
        try:
            # Placeholder: Normalize audio
            max_val = torch.max(torch.abs(waveform))
            if max_val > 0:
                enhanced = waveform / max_val * 0.95

            logger.info("Applied speech enhancement")
            return enhanced

        except Exception as e:
            logger.error(f"Speech enhancement failed: {e}")
            return waveform

    async def apply_voice_isolation(
        self,
        waveform: torch.Tensor,
        sample_rate: int
    ) -> torch.Tensor:
        """
        Isolate vocals using Demucs

        NOTE: Placeholder implementation. Integrate Demucs in production.
        """
        try:
            # Placeholder: Return original
            # In production, use Demucs for source separation
            logger.info("Applied voice isolation (placeholder)")
            return waveform

        except Exception as e:
            logger.error(f"Voice isolation failed: {e}")
            return waveform

    async def apply_click_removal(
        self,
        waveform: torch.Tensor,
        sample_rate: int
    ) -> torch.Tensor:
        """
        Remove clicks and pops

        Uses median filtering to detect and remove impulse noise
        """
        try:
            # Simple click removal using median filter
            from scipy.signal import medfilt

            audio_np = waveform.cpu().numpy()
            if audio_np.ndim > 1:
                audio_np = audio_np[0]

            # Detect clicks using first derivative
            diff = np.diff(audio_np)
            threshold = np.std(diff) * 3

            # Apply median filter to detected clicks
            filtered = audio_np.copy()
            clicks = np.where(np.abs(diff) > threshold)[0]

            for click_idx in clicks:
                start = max(0, click_idx - 2)
                end = min(len(filtered), click_idx + 3)
                filtered[start:end] = medfilt(audio_np[start:end], kernel_size=5)

            result = torch.from_numpy(filtered).unsqueeze(0).to(self.device)
            logger.info(f"Removed {len(clicks)} clicks")
            return result

        except Exception as e:
            logger.error(f"Click removal failed: {e}")
            return waveform

    async def apply_spectral_repair(
        self,
        waveform: torch.Tensor,
        sample_rate: int
    ) -> torch.Tensor:
        """
        Repair spectral defects

        NOTE: Placeholder. Implement advanced spectral repair in production.
        """
        try:
            # Placeholder implementation
            logger.info("Applied spectral repair (placeholder)")
            return waveform

        except Exception as e:
            logger.error(f"Spectral repair failed: {e}")
            return waveform

    async def apply_dehum(
        self,
        waveform: torch.Tensor,
        sample_rate: int,
        frequency: int = 60
    ) -> torch.Tensor:
        """
        Remove hum at specified frequency (50Hz or 60Hz)

        Uses notch filter to remove electrical interference
        """
        try:
            from scipy.signal import iirnotch, filtfilt

            audio_np = waveform.cpu().numpy()
            if audio_np.ndim > 1:
                audio_np = audio_np[0]

            # Design notch filter
            quality_factor = 30.0
            b, a = iirnotch(frequency, quality_factor, sample_rate)

            # Apply filter
            filtered = filtfilt(b, a, audio_np)

            # Also filter harmonics
            for harmonic in [2, 3, 4]:
                b, a = iirnotch(frequency * harmonic, quality_factor, sample_rate)
                filtered = filtfilt(b, a, filtered)

            result = torch.from_numpy(filtered).unsqueeze(0).to(self.device)
            logger.info(f"Removed {frequency}Hz hum and harmonics")
            return result

        except Exception as e:
            logger.error(f"De-hum failed: {e}")
            return waveform

    async def apply_super_resolution(
        self,
        waveform: torch.Tensor,
        current_sr: int,
        target_sr: int
    ) -> torch.Tensor:
        """
        Upsample audio using AI super-resolution

        NOTE: For production, integrate AudioSR or similar model
        """
        try:
            # Use torchaudio resampling for now
            # In production, use AudioSR for better quality
            resampler = torchaudio.transforms.Resample(
                orig_freq=current_sr,
                new_freq=target_sr
            ).to(self.device)

            upsampled = resampler(waveform)
            logger.info(f"Upsampled from {current_sr}Hz to {target_sr}Hz")
            return upsampled

        except Exception as e:
            logger.error(f"Super-resolution failed: {e}")
            return waveform

    async def apply_dynamic_range_enhancement(
        self,
        waveform: torch.Tensor,
        sample_rate: int
    ) -> torch.Tensor:
        """
        Enhance dynamic range using compression/expansion
        """
        try:
            # Simple dynamic range compression
            threshold = 0.5
            ratio = 3.0

            audio = waveform.clone()
            mask = torch.abs(audio) > threshold

            # Compress peaks
            compressed = torch.where(
                mask,
                threshold + (audio - threshold * torch.sign(audio)) / ratio,
                audio
            )

            logger.info("Applied dynamic range enhancement")
            return compressed

        except Exception as e:
            logger.error(f"Dynamic range enhancement failed: {e}")
            return waveform

    def cleanup(self):
        """Clean up loaded models to free memory"""
        self.models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Cleaned up models and freed GPU memory")

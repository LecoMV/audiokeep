"""
Audio Processing Celery Tasks
Main audio processing pipeline
"""
from celery import Task
from decimal import Decimal
import logging
import torch
import torchaudio
import numpy as np
from typing import Dict, Any
import io

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.job_service import JobService
from app.services.storage_service import StorageService
from app.models.job import JobStatus
from app.ai_models.model_manager import ModelManager

logger = logging.getLogger(__name__)


class AudioProcessingTask(Task):
    """Base task for audio processing with model caching"""
    _model_manager = None

    @property
    def model_manager(self):
        if self._model_manager is None:
            self._model_manager = ModelManager()
        return self._model_manager


@celery_app.task(base=AudioProcessingTask, bind=True, name="app.services.audio_processing.process_audio_task")
def process_audio_task(self, job_id: str):
    """
    Process audio file with AI models

    This is the main Celery task that orchestrates the audio processing pipeline
    """
    import asyncio
    return asyncio.run(process_audio_async(self, job_id))


async def process_audio_async(task, job_id: str):
    """Async audio processing workflow"""
    async with AsyncSessionLocal() as db:
        job_service = JobService(db)
        storage_service = StorageService()

        try:
            # Update job status
            await job_service.update_job_status(job_id, JobStatus.PROCESSING)

            # Get job details
            job = await job_service.get_job(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")

            logger.info(f"Starting processing for job {job_id}")

            # Download input file
            audio_data = await storage_service.download_file(job.input_file_url)

            # Load audio
            waveform, sample_rate = torchaudio.load(io.BytesIO(audio_data))

            # Move to GPU if available
            device = torch.device(settings.TORCH_DEVICE)
            waveform = waveform.to(device)

            logger.info(f"Loaded audio: {waveform.shape}, SR: {sample_rate}, Device: {device}")

            # Process audio through pipeline
            processed_audio = await process_audio_pipeline(
                waveform=waveform,
                sample_rate=sample_rate,
                settings=job.settings,
                model_manager=task.model_manager
            )

            # Calculate quality metrics
            metrics = calculate_quality_metrics(waveform.cpu(), processed_audio.cpu(), sample_rate)

            # Export processed audio
            output_buffer = io.BytesIO()
            output_format = job.settings.get('output_format', 'wav')

            if output_format == 'wav':
                torchaudio.save(
                    output_buffer,
                    processed_audio.cpu(),
                    sample_rate,
                    format='wav'
                )
            elif output_format == 'flac':
                torchaudio.save(
                    output_buffer,
                    processed_audio.cpu(),
                    sample_rate,
                    format='flac'
                )
            elif output_format == 'mp3':
                # For MP3, we need to use a different library or FFmpeg
                # For now, save as WAV and convert later
                torchaudio.save(
                    output_buffer,
                    processed_audio.cpu(),
                    sample_rate,
                    format='wav'
                )

            output_buffer.seek(0)

            # Upload processed file
            output_filename = f"processed_{job.original_filename}"
            output_key = await storage_service.upload_file(
                file_content=output_buffer.read(),
                filename=output_filename,
                user_id=job.user_id,
                folder="processed"
            )

            # Generate presigned URL
            output_url = storage_service.generate_presigned_url(output_key)

            # Complete job
            await job_service.complete_job(
                job_id=job_id,
                output_file_url=output_url,
                quality_metrics=metrics,
                credits_used=job.credits_estimated  # In production, calculate actual credits used
            )

            logger.info(f"Successfully processed job {job_id}")
            return {"status": "completed", "job_id": job_id}

        except Exception as e:
            logger.error(f"Failed to process job {job_id}: {e}", exc_info=True)

            # Mark job as failed
            await job_service.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=str(e)
            )

            raise


async def process_audio_pipeline(
    waveform: torch.Tensor,
    sample_rate: int,
    settings: Dict[str, Any],
    model_manager: 'ModelManager'
) -> torch.Tensor:
    """
    Audio processing pipeline

    Applies various AI models based on settings
    """
    processed = waveform

    # Stage 1: Noise Reduction
    if settings.get('noise_reduction'):
        logger.info("Applying noise reduction...")
        strength = settings.get('noise_reduction_strength', 0.5)
        processed = await model_manager.apply_noise_reduction(
            processed,
            sample_rate,
            strength=strength
        )

    # Stage 2: Speech Enhancement
    if settings.get('speech_enhancement'):
        logger.info("Applying speech enhancement...")
        processed = await model_manager.apply_speech_enhancement(
            processed,
            sample_rate
        )

    # Stage 3: Voice Isolation (Source Separation)
    if settings.get('voice_isolation'):
        logger.info("Applying voice isolation...")
        processed = await model_manager.apply_voice_isolation(
            processed,
            sample_rate
        )

    # Stage 4: Click/Pop Removal
    if settings.get('click_removal'):
        logger.info("Removing clicks and pops...")
        processed = await model_manager.apply_click_removal(
            processed,
            sample_rate
        )

    # Stage 5: Spectral Repair
    if settings.get('spectral_repair'):
        logger.info("Applying spectral repair...")
        processed = await model_manager.apply_spectral_repair(
            processed,
            sample_rate
        )

    # Stage 6: De-hum
    if settings.get('dehum'):
        logger.info("Removing hum...")
        processed = await model_manager.apply_dehum(
            processed,
            sample_rate
        )

    # Stage 7: Bandwidth Extension
    if settings.get('bandwidth_extension'):
        logger.info("Extending bandwidth...")
        target_sr = settings.get('target_sample_rate', 48000)
        processed = await model_manager.apply_super_resolution(
            processed,
            sample_rate,
            target_sr
        )
        sample_rate = target_sr

    # Stage 8: Dynamic Range Enhancement
    if settings.get('dynamic_range_enhancement'):
        logger.info("Enhancing dynamic range...")
        processed = await model_manager.apply_dynamic_range_enhancement(
            processed,
            sample_rate
        )

    return processed


def calculate_quality_metrics(
    original: torch.Tensor,
    processed: torch.Tensor,
    sample_rate: int
) -> Dict[str, float]:
    """Calculate audio quality metrics"""
    import pyloudnorm as pyln

    # Convert to numpy
    original_np = original.numpy()[0] if original.dim() > 1 else original.numpy()
    processed_np = processed.numpy()[0] if processed.dim() > 1 else processed.numpy()

    metrics = {}

    try:
        # Loudness
        meter = pyln.Meter(sample_rate)
        metrics['loudness_lufs'] = float(meter.integrated_loudness(processed_np))

        # Signal-to-Noise Ratio (simplified estimation)
        signal_power = np.mean(processed_np ** 2)
        noise_estimate = np.mean((original_np - processed_np) ** 2)
        if noise_estimate > 0:
            snr = 10 * np.log10(signal_power / noise_estimate)
            metrics['snr_db'] = float(snr)

        # Peak amplitude
        metrics['peak_amplitude'] = float(np.max(np.abs(processed_np)))

        # Dynamic range
        rms = np.sqrt(np.mean(processed_np ** 2))
        peak = np.max(np.abs(processed_np))
        if rms > 0:
            dr = 20 * np.log10(peak / rms)
            metrics['dynamic_range_db'] = float(dr)

    except Exception as e:
        logger.error(f"Failed to calculate metrics: {e}")

    return metrics

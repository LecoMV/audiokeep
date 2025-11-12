#!/usr/bin/env python3
"""
GPU Benchmark Script for AudioKeep
Tests GPU performance for audio processing workloads
"""
import torch
import torchaudio
import time
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPUBenchmark:
    """Benchmark GPU performance for audio processing"""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.results = {}

        logger.info("=" * 70)
        logger.info("AudioKeep GPU Benchmark")
        logger.info("=" * 70)
        logger.info(f"Device: {self.device}")

        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Version: {torch.version.cuda}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            logger.warning("WARNING: CUDA not available, running on CPU")

    def generate_test_audio(self, duration: int, sample_rate: int = 48000) -> torch.Tensor:
        """Generate test audio signal"""
        num_samples = duration * sample_rate

        # Generate sine wave with noise
        t = torch.linspace(0, duration, num_samples)
        frequency = 440  # A4 note
        audio = torch.sin(2 * np.pi * frequency * t)
        noise = torch.randn(num_samples) * 0.1
        audio = audio + noise

        # Add stereo dimension
        audio = audio.unsqueeze(0)  # [1, num_samples]

        return audio

    def benchmark_memory_transfer(self):
        """Benchmark CPU to GPU memory transfer"""
        logger.info("\n" + "=" * 70)
        logger.info("Memory Transfer Benchmark")
        logger.info("=" * 70)

        if not torch.cuda.is_available():
            logger.warning("Skipping - CUDA not available")
            return

        sizes = [1, 5, 10, 30, 60]  # minutes
        results = []

        for duration in sizes:
            audio = self.generate_test_audio(duration)
            size_mb = audio.element_size() * audio.nelement() / (1024**2)

            # Benchmark transfer
            start = time.time()
            audio_gpu = audio.to(self.device)
            torch.cuda.synchronize()
            transfer_time = time.time() - start

            speed = size_mb / transfer_time if transfer_time > 0 else 0
            results.append({
                'duration': duration,
                'size_mb': size_mb,
                'time': transfer_time,
                'speed': speed
            })

            logger.info(f"{duration:2d} min | {size_mb:6.2f} MB | {transfer_time:.4f}s | {speed:.2f} MB/s")

            # Cleanup
            del audio_gpu
            torch.cuda.empty_cache()

        self.results['memory_transfer'] = results

    def benchmark_resampling(self):
        """Benchmark audio resampling on GPU"""
        logger.info("\n" + "=" * 70)
        logger.info("Resampling Benchmark")
        logger.info("=" * 70)

        audio = self.generate_test_audio(60).to(self.device)  # 1 minute

        resample_configs = [
            (16000, 48000, "Upsample 16kHz → 48kHz"),
            (44100, 48000, "Upsample 44.1kHz → 48kHz"),
            (48000, 96000, "Upsample 48kHz → 96kHz"),
            (48000, 192000, "Upsample 48kHz → 192kHz"),
        ]

        results = []

        for orig_sr, target_sr, description in resample_configs:
            resampler = torchaudio.transforms.Resample(
                orig_freq=orig_sr,
                new_freq=target_sr
            ).to(self.device)

            # Warmup
            _ = resampler(audio)
            if torch.cuda.is_available():
                torch.cuda.synchronize()

            # Benchmark
            iterations = 10
            start = time.time()
            for _ in range(iterations):
                _ = resampler(audio)

            if torch.cuda.is_available():
                torch.cuda.synchronize()

            elapsed = time.time() - start
            avg_time = elapsed / iterations
            rtf = avg_time / 60  # Real-time factor (60 seconds audio)

            results.append({
                'config': description,
                'time': avg_time,
                'rtf': rtf
            })

            logger.info(f"{description:30s} | {avg_time:.4f}s | RTF: {rtf:.4f}x")

        self.results['resampling'] = results

    def benchmark_noise_gate(self):
        """Benchmark simple noise gate operation"""
        logger.info("\n" + "=" * 70)
        logger.info("Noise Gate Benchmark")
        logger.info("=" * 70)

        durations = [1, 5, 10, 30, 60]  # minutes
        results = []

        for duration in durations:
            audio = self.generate_test_audio(duration).to(self.device)

            # Warmup
            threshold = 0.01
            _ = audio * (torch.abs(audio) > threshold).float()
            if torch.cuda.is_available():
                torch.cuda.synchronize()

            # Benchmark
            iterations = 5
            start = time.time()
            for _ in range(iterations):
                filtered = audio * (torch.abs(audio) > threshold).float()

            if torch.cuda.is_available():
                torch.cuda.synchronize()

            elapsed = time.time() - start
            avg_time = elapsed / iterations
            rtf = avg_time / (duration * 60)

            results.append({
                'duration': duration,
                'time': avg_time,
                'rtf': rtf
            })

            logger.info(f"{duration:2d} min | {avg_time:.4f}s | RTF: {rtf:.6f}x")

            del audio, filtered
            torch.cuda.empty_cache()

        self.results['noise_gate'] = results

    def benchmark_batch_processing(self):
        """Benchmark batch processing capability"""
        logger.info("\n" + "=" * 70)
        logger.info("Batch Processing Benchmark")
        logger.info("=" * 70)

        if not torch.cuda.is_available():
            logger.warning("Skipping - CUDA not available")
            return

        batch_sizes = [1, 2, 4, 8]
        duration = 5  # 5 minutes per file
        results = []

        for batch_size in batch_sizes:
            try:
                # Create batch
                audio_batch = torch.stack([
                    self.generate_test_audio(duration)
                    for _ in range(batch_size)
                ]).to(self.device)

                # Simple processing (noise gate)
                start = time.time()
                threshold = 0.01
                processed = audio_batch * (torch.abs(audio_batch) > threshold).float()
                torch.cuda.synchronize()

                elapsed = time.time() - start
                per_file = elapsed / batch_size
                rtf = per_file / (duration * 60)

                # Check memory
                memory_used = torch.cuda.memory_allocated() / (1024**3)
                memory_cached = torch.cuda.memory_reserved() / (1024**3)

                results.append({
                    'batch_size': batch_size,
                    'time': elapsed,
                    'per_file': per_file,
                    'rtf': rtf,
                    'memory_gb': memory_used
                })

                logger.info(
                    f"Batch {batch_size} | {elapsed:.4f}s total | "
                    f"{per_file:.4f}s/file | RTF: {rtf:.6f}x | "
                    f"Mem: {memory_used:.2f}GB"
                )

                del audio_batch, processed
                torch.cuda.empty_cache()

            except RuntimeError as e:
                logger.error(f"Batch {batch_size} - Out of memory: {e}")
                torch.cuda.empty_cache()
                break

        self.results['batch_processing'] = results

    def benchmark_mixed_precision(self):
        """Benchmark FP16 vs FP32 performance"""
        logger.info("\n" + "=" * 70)
        logger.info("Mixed Precision Benchmark")
        logger.info("=" * 70)

        if not torch.cuda.is_available():
            logger.warning("Skipping - CUDA not available")
            return

        audio = self.generate_test_audio(10).to(self.device)  # 10 minutes

        precisions = [
            ('FP32', torch.float32),
            ('FP16', torch.float16),
        ]

        results = []

        for name, dtype in precisions:
            audio_typed = audio.to(dtype)

            # Benchmark
            iterations = 10
            start = time.time()
            for _ in range(iterations):
                # Simple operation
                processed = audio_typed * 0.95
                processed = processed + torch.randn_like(processed) * 0.01

            torch.cuda.synchronize()
            elapsed = time.time() - start
            avg_time = elapsed / iterations

            memory_used = torch.cuda.memory_allocated() / (1024**3)

            results.append({
                'precision': name,
                'time': avg_time,
                'memory_gb': memory_used
            })

            logger.info(f"{name} | {avg_time:.4f}s | Memory: {memory_used:.2f}GB")

            del audio_typed, processed
            torch.cuda.empty_cache()

        self.results['mixed_precision'] = results

    def print_summary(self):
        """Print benchmark summary"""
        logger.info("\n" + "=" * 70)
        logger.info("Benchmark Summary")
        logger.info("=" * 70)

        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            logger.info(f"CUDA Cores: {torch.cuda.get_device_properties(0).multi_processor_count}")

        logger.info("\nKey Findings:")

        # Resampling performance
        if 'resampling' in self.results:
            avg_rtf = np.mean([r['rtf'] for r in self.results['resampling']])
            logger.info(f"- Average Resampling RTF: {avg_rtf:.4f}x")
            logger.info(f"  (< 0.1x is excellent, < 0.5x is good)")

        # Noise gate performance
        if 'noise_gate' in self.results:
            best_rtf = min([r['rtf'] for r in self.results['noise_gate']])
            logger.info(f"- Best Noise Gate RTF: {best_rtf:.6f}x")
            logger.info(f"  (Can process {1/best_rtf:.0f}x faster than real-time)")

        # Batch processing
        if 'batch_processing' in self.results and self.results['batch_processing']:
            max_batch = max([r['batch_size'] for r in self.results['batch_processing']])
            logger.info(f"- Max Batch Size: {max_batch}")
            logger.info(f"  (Limited by GPU memory)")

        logger.info("\nRecommendations:")
        logger.info("- Enable mixed precision (FP16) for 2x speedup")
        logger.info("- Use batch processing for multiple files")
        logger.info("- Monitor GPU memory usage during production")
        logger.info("- Set worker concurrency based on GPU memory")

        logger.info("\n" + "=" * 70)

    def run(self):
        """Run all benchmarks"""
        self.benchmark_memory_transfer()
        self.benchmark_resampling()
        self.benchmark_noise_gate()
        self.benchmark_batch_processing()
        self.benchmark_mixed_precision()
        self.print_summary()

        return self.results


def main():
    """Main entry point"""
    benchmark = GPUBenchmark()
    results = benchmark.run()

    # Save results
    import json
    output_file = Path('benchmark_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

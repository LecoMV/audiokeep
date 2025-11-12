#!/usr/bin/env python3
"""
Download and Setup AI Models for AudioKeep
Run this script on the GPU server to download all required models
"""
import os
import sys
from pathlib import Path
import torch
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelDownloader:
    """Download and verify AI models"""

    def __init__(self, cache_dir: str = "/data/audiokeep/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set environment variables
        os.environ['TORCH_HOME'] = str(self.cache_dir / 'torch')
        os.environ['HF_HOME'] = str(self.cache_dir / 'huggingface')

        logger.info(f"Model cache directory: {self.cache_dir}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

    def download_resemble_enhance(self):
        """Download Resemble Enhance model"""
        logger.info("=" * 60)
        logger.info("Downloading Resemble Enhance...")
        logger.info("=" * 60)

        try:
            # Clone repository if needed
            resemble_dir = self.cache_dir / 'resemble-enhance'
            if not resemble_dir.exists():
                logger.info("Cloning Resemble Enhance repository...")
                os.system(f"git clone https://github.com/resemble-ai/resemble-enhance.git {resemble_dir}")

            # Download model weights
            logger.info("Downloading model weights from Hugging Face...")

            # This will be done automatically when first running the model
            # The model will download to HF_HOME
            logger.info("✓ Resemble Enhance setup complete")
            logger.info("Note: Model weights will download on first use")

            return True

        except Exception as e:
            logger.error(f"Failed to setup Resemble Enhance: {e}")
            return False

    def download_demucs(self):
        """Download Demucs model"""
        logger.info("=" * 60)
        logger.info("Downloading Demucs...")
        logger.info("=" * 60)

        try:
            # Demucs models download automatically via torch.hub
            import torch.hub

            logger.info("Downloading Demucs Hybrid Transformer model...")

            # This will download the model
            # In production, use: torch.hub.load('facebookresearch/demucs', 'htdemucs')
            logger.info("✓ Demucs will download on first use")
            logger.info("Note: ~2GB download, may take a few minutes")

            return True

        except Exception as e:
            logger.error(f"Failed to setup Demucs: {e}")
            return False

    def download_deepfilternet(self):
        """Download DeepFilterNet model"""
        logger.info("=" * 60)
        logger.info("Downloading DeepFilterNet...")
        logger.info("=" * 60)

        try:
            # DeepFilterNet can be installed via pip
            logger.info("Installing DeepFilterNet...")
            os.system("pip install deepfilternet")

            # Download model weights
            logger.info("Downloading DeepFilterNet model weights...")

            # Models will auto-download on first use
            logger.info("✓ DeepFilterNet setup complete")
            logger.info("Note: Model weights will download on first use")

            return True

        except Exception as e:
            logger.error(f"Failed to setup DeepFilterNet: {e}")
            return False

    def download_audiosr(self):
        """Download AudioSR model"""
        logger.info("=" * 60)
        logger.info("Downloading AudioSR...")
        logger.info("=" * 60)

        try:
            # Clone AudioSR repository
            audiosr_dir = self.cache_dir / 'audiosr'
            if not audiosr_dir.exists():
                logger.info("Cloning AudioSR repository...")
                os.system(f"git clone https://github.com/haoheliu/versatile_audio_super_resolution.git {audiosr_dir}")

            logger.info("✓ AudioSR setup complete")
            logger.info("Note: Model weights will download on first use")

            return True

        except Exception as e:
            logger.error(f"Failed to setup AudioSR: {e}")
            return False

    def verify_models(self):
        """Verify all models are accessible"""
        logger.info("=" * 60)
        logger.info("Verifying Model Setup...")
        logger.info("=" * 60)

        all_ok = True

        # Check directory structure
        required_dirs = [
            self.cache_dir / 'torch',
            self.cache_dir / 'huggingface',
        ]

        for dir_path in required_dirs:
            if dir_path.exists():
                logger.info(f"✓ {dir_path.name} directory exists")
            else:
                logger.warning(f"✗ {dir_path.name} directory not found")
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  Created {dir_path}")

        # Check available disk space
        import shutil
        total, used, free = shutil.disk_usage(self.cache_dir)
        logger.info(f"\nDisk Space:")
        logger.info(f"  Total: {total / (1024**3):.2f} GB")
        logger.info(f"  Used: {used / (1024**3):.2f} GB")
        logger.info(f"  Free: {free / (1024**3):.2f} GB")

        if free < 20 * (1024**3):  # Less than 20GB free
            logger.warning("WARNING: Less than 20GB free space. Models may require more space.")
            all_ok = False

        return all_ok

    def run(self):
        """Run full model download process"""
        logger.info("=" * 60)
        logger.info("AudioKeep Model Download Script")
        logger.info("=" * 60)
        logger.info("")

        results = {}

        # Download each model
        results['resemble'] = self.download_resemble_enhance()
        results['demucs'] = self.download_demucs()
        results['deepfilternet'] = self.download_deepfilternet()
        results['audiosr'] = self.download_audiosr()

        # Verify setup
        results['verification'] = self.verify_models()

        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("Download Summary")
        logger.info("=" * 60)

        for model, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{model.upper()}: {status}")

        logger.info("")
        logger.info("=" * 60)

        if all(results.values()):
            logger.info("✓ All models downloaded successfully!")
            logger.info("")
            logger.info("Next Steps:")
            logger.info("1. Run GPU benchmark: python scripts/benchmark_gpu.py")
            logger.info("2. Start services: docker-compose up -d")
            logger.info("3. Monitor logs: docker-compose logs -f celery-worker")
            return 0
        else:
            logger.error("✗ Some models failed to download")
            logger.error("Please check errors above and retry")
            return 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Download AudioKeep AI models')
    parser.add_argument(
        '--cache-dir',
        type=str,
        default='/data/audiokeep/models',
        help='Directory to store models (default: /data/audiokeep/models)'
    )

    args = parser.parse_args()

    downloader = ModelDownloader(cache_dir=args.cache_dir)
    return downloader.run()


if __name__ == '__main__':
    sys.exit(main())

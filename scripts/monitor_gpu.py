#!/usr/bin/env python3
"""
GPU Health Monitoring Script
Continuously monitor GPU health and performance
"""
import subprocess
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPUMonitor:
    """Monitor GPU health and performance"""

    def __init__(self, log_dir: str = "/var/log/audiokeep"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.log_dir / "gpu_metrics.jsonl"
        self.alerts_file = self.log_dir / "gpu_alerts.log"

        # Thresholds for alerts
        self.thresholds = {
            'temperature': 85,  # Celsius
            'memory_usage': 90,  # Percent
            'power_usage': 95,  # Percent of max
            'utilization': 95,  # Percent
        }

    def get_gpu_metrics(self) -> List[Dict]:
        """Get current GPU metrics using nvidia-smi"""
        try:
            cmd = [
                'nvidia-smi',
                '--query-gpu=index,name,temperature.gpu,utilization.gpu,'
                'utilization.memory,memory.used,memory.total,power.draw,'
                'power.limit,fan.speed,pstate',
                '--format=csv,noheader,nounits'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')

            metrics = []
            for line in lines:
                if not line.strip():
                    continue

                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 11:
                    gpu_index, name, temp, util_gpu, util_mem, mem_used, mem_total, power_draw, power_limit, fan_speed, pstate = parts

                    # Calculate percentages
                    mem_used_gb = float(mem_used) / 1024
                    mem_total_gb = float(mem_total) / 1024
                    mem_percent = (float(mem_used) / float(mem_total)) * 100 if float(mem_total) > 0 else 0
                    power_percent = (float(power_draw) / float(power_limit)) * 100 if float(power_limit) > 0 else 0

                    metrics.append({
                        'timestamp': datetime.now().isoformat(),
                        'gpu_index': int(gpu_index),
                        'name': name,
                        'temperature_c': float(temp),
                        'utilization_gpu_percent': float(util_gpu),
                        'utilization_memory_percent': float(util_mem),
                        'memory_used_mb': float(mem_used),
                        'memory_total_mb': float(mem_total),
                        'memory_used_gb': round(mem_used_gb, 2),
                        'memory_total_gb': round(mem_total_gb, 2),
                        'memory_percent': round(mem_percent, 2),
                        'power_draw_w': float(power_draw),
                        'power_limit_w': float(power_limit),
                        'power_percent': round(power_percent, 2),
                        'fan_speed_percent': float(fan_speed) if fan_speed != 'N/A' else 0,
                        'performance_state': pstate
                    })

            return metrics

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get GPU metrics: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing GPU metrics: {e}")
            return []

    def check_alerts(self, metrics: List[Dict]) -> List[Dict]:
        """Check for alert conditions"""
        alerts = []

        for gpu in metrics:
            gpu_id = gpu['gpu_index']

            # Temperature alert
            if gpu['temperature_c'] > self.thresholds['temperature']:
                alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'gpu': gpu_id,
                    'type': 'HIGH_TEMPERATURE',
                    'severity': 'WARNING' if gpu['temperature_c'] < 90 else 'CRITICAL',
                    'value': gpu['temperature_c'],
                    'threshold': self.thresholds['temperature'],
                    'message': f"GPU {gpu_id} temperature {gpu['temperature_c']}°C exceeds threshold {self.thresholds['temperature']}°C"
                })

            # Memory usage alert
            if gpu['memory_percent'] > self.thresholds['memory_usage']:
                alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'gpu': gpu_id,
                    'type': 'HIGH_MEMORY_USAGE',
                    'severity': 'WARNING',
                    'value': gpu['memory_percent'],
                    'threshold': self.thresholds['memory_usage'],
                    'message': f"GPU {gpu_id} memory usage {gpu['memory_percent']:.1f}% exceeds threshold {self.thresholds['memory_usage']}%"
                })

            # Power usage alert
            if gpu['power_percent'] > self.thresholds['power_usage']:
                alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'gpu': gpu_id,
                    'type': 'HIGH_POWER_USAGE',
                    'severity': 'INFO',
                    'value': gpu['power_percent'],
                    'threshold': self.thresholds['power_usage'],
                    'message': f"GPU {gpu_id} power usage {gpu['power_percent']:.1f}% exceeds threshold {self.thresholds['power_usage']}%"
                })

            # Utilization alert (sustained high usage might indicate stuck process)
            if gpu['utilization_gpu_percent'] > self.thresholds['utilization']:
                alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'gpu': gpu_id,
                    'type': 'HIGH_UTILIZATION',
                    'severity': 'INFO',
                    'value': gpu['utilization_gpu_percent'],
                    'threshold': self.thresholds['utilization'],
                    'message': f"GPU {gpu_id} utilization {gpu['utilization_gpu_percent']:.1f}% (sustained high usage)"
                })

        return alerts

    def log_metrics(self, metrics: List[Dict]):
        """Log metrics to file"""
        try:
            with open(self.metrics_file, 'a') as f:
                for metric in metrics:
                    f.write(json.dumps(metric) + '\n')
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")

    def log_alerts(self, alerts: List[Dict]):
        """Log alerts to file and console"""
        if not alerts:
            return

        try:
            with open(self.alerts_file, 'a') as f:
                for alert in alerts:
                    # Log to file
                    f.write(json.dumps(alert) + '\n')

                    # Log to console
                    severity = alert['severity']
                    if severity == 'CRITICAL':
                        logger.error(alert['message'])
                    elif severity == 'WARNING':
                        logger.warning(alert['message'])
                    else:
                        logger.info(alert['message'])

        except Exception as e:
            logger.error(f"Failed to log alerts: {e}")

    def print_summary(self, metrics: List[Dict]):
        """Print summary to console"""
        if not metrics:
            logger.warning("No GPU metrics available")
            return

        logger.info("=" * 80)
        logger.info("GPU Status Summary")
        logger.info("=" * 80)

        for gpu in metrics:
            logger.info(
                f"GPU {gpu['gpu_index']} ({gpu['name']}): "
                f"Temp: {gpu['temperature_c']}°C | "
                f"GPU: {gpu['utilization_gpu_percent']:.1f}% | "
                f"Mem: {gpu['memory_used_gb']:.1f}GB/{gpu['memory_total_gb']:.1f}GB ({gpu['memory_percent']:.1f}%) | "
                f"Power: {gpu['power_draw_w']:.1f}W/{gpu['power_limit_w']:.1f}W ({gpu['power_percent']:.1f}%) | "
                f"Fan: {gpu['fan_speed_percent']:.0f}% | "
                f"State: {gpu['performance_state']}"
            )

        logger.info("=" * 80)

    def monitor_continuous(self, interval: int = 10):
        """Continuously monitor GPU"""
        logger.info(f"Starting continuous GPU monitoring (interval={interval}s)")
        logger.info(f"Logging to: {self.log_dir}")

        try:
            while True:
                # Get metrics
                metrics = self.get_gpu_metrics()

                if metrics:
                    # Check for alerts
                    alerts = self.check_alerts(metrics)

                    # Log everything
                    self.log_metrics(metrics)
                    if alerts:
                        self.log_alerts(alerts)

                    # Print summary
                    self.print_summary(metrics)

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

    def get_health_status(self) -> Dict:
        """Get current health status"""
        metrics = self.get_gpu_metrics()

        if not metrics:
            return {
                'status': 'ERROR',
                'message': 'Unable to get GPU metrics',
                'gpus': []
            }

        alerts = self.check_alerts(metrics)

        # Determine overall status
        if any(a['severity'] == 'CRITICAL' for a in alerts):
            status = 'CRITICAL'
        elif any(a['severity'] == 'WARNING' for a in alerts):
            status = 'WARNING'
        else:
            status = 'HEALTHY'

        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'gpus': metrics,
            'alerts': alerts,
            'alert_count': len(alerts)
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='GPU Health Monitor')
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Monitoring interval in seconds (default: 10)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for cron jobs)'
    )
    parser.add_argument(
        '--log-dir',
        type=str,
        default='/var/log/audiokeep',
        help='Log directory (default: /var/log/audiokeep)'
    )

    args = parser.parse_args()

    monitor = GPUMonitor(log_dir=args.log_dir)

    if args.once:
        # Single check
        metrics = monitor.get_gpu_metrics()
        if metrics:
            alerts = monitor.check_alerts(metrics)
            monitor.log_metrics(metrics)
            monitor.log_alerts(alerts)
            monitor.print_summary(metrics)

        # Exit with status code based on alerts
        if any(a['severity'] == 'CRITICAL' for a in alerts):
            return 2
        elif any(a['severity'] == 'WARNING' for a in alerts):
            return 1
        return 0
    else:
        # Continuous monitoring
        monitor.monitor_continuous(interval=args.interval)
        return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

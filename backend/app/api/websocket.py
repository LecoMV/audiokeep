"""
WebSocket Support for Real-Time Job Status Updates
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import logging
import asyncio

from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        # Map of job_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of websocket -> user_id for authentication
        self.connection_users: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, job_id: str, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()

        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()

        self.active_connections[job_id].add(websocket)
        self.connection_users[websocket] = user_id

        logger.info(f"WebSocket connected for job {job_id} (user: {user_id})")

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove WebSocket connection"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)

            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

        if websocket in self.connection_users:
            del self.connection_users[websocket]

        logger.info(f"WebSocket disconnected for job {job_id}")

    async def send_status_update(self, job_id: str, status_data: dict):
        """Send status update to all connections watching this job"""
        if job_id not in self.active_connections:
            return

        # Convert to JSON
        message = json.dumps(status_data)

        # Send to all connections
        dead_connections = set()
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket: {e}")
                dead_connections.add(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection, job_id)

    async def send_progress_update(
        self,
        job_id: str,
        progress: float,
        stage: str,
        message: str = None
    ):
        """Send progress update"""
        await self.send_status_update(job_id, {
            'type': 'progress',
            'job_id': job_id,
            'progress': progress,
            'stage': stage,
            'message': message
        })

    async def send_completion(self, job_id: str, output_url: str, metrics: dict):
        """Send job completion notification"""
        await self.send_status_update(job_id, {
            'type': 'completed',
            'job_id': job_id,
            'output_url': output_url,
            'metrics': metrics
        })

    async def send_error(self, job_id: str, error_message: str):
        """Send error notification"""
        await self.send_status_update(job_id, {
            'type': 'error',
            'job_id': job_id,
            'error': error_message
        })


# Global connection manager
manager = ConnectionManager()


async def websocket_job_status(
    websocket: WebSocket,
    job_id: str,
    token: str  # JWT token passed as query parameter
):
    """
    WebSocket endpoint for job status updates

    Usage:
    ```javascript
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/jobs/${jobId}?token=${accessToken}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Update:', data);

        if (data.type === 'progress') {
            updateProgressBar(data.progress);
        } else if (data.type === 'completed') {
            showDownloadButton(data.output_url);
        }
    };
    ```
    """
    from app.core.security import decode_token
    from app.db.session import AsyncSessionLocal
    from app.services.job_service import JobService

    # Authenticate using token
    payload = decode_token(token)
    if not payload or payload.get('type') != 'access':
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id = payload.get('sub')

    # Verify job exists and belongs to user
    async with AsyncSessionLocal() as db:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)

        if not job:
            await websocket.close(code=1008, reason="Job not found")
            return

        if job.user_id != user_id:
            await websocket.close(code=1008, reason="Unauthorized")
            return

    # Connect WebSocket
    await manager.connect(websocket, job_id, user_id)

    try:
        # Send initial status
        async with AsyncSessionLocal() as db:
            job_service = JobService(db)
            job = await job_service.get_job(job_id)

            await websocket.send_json({
                'type': 'status',
                'job_id': job_id,
                'status': job.status.value if hasattr(job.status, 'value') else str(job.status),
                'progress': 0.0 if job.status.value == 'pending' else 0.5 if job.status.value == 'processing' else 1.0
            })

        # Keep connection alive and listen for disconnect
        while True:
            # Wait for messages (ping/pong to keep alive)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back for keepalive
                await websocket.send_json({'type': 'pong'})
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({'type': 'ping'})
            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, job_id)


# Export for use in main.py
__all__ = ['manager', 'websocket_job_status']

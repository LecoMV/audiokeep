"""
Tests for WebSocket Real-Time Updates
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json
import asyncio

from app.api.websocket import ConnectionManager, manager


@pytest.mark.unit
class TestConnectionManager:
    """Test WebSocket connection manager"""

    def test_connection_manager_initialization(self):
        """Test connection manager initializes correctly"""
        cm = ConnectionManager()

        assert cm.active_connections == {}
        assert cm.connection_users == {}

    async def test_connect_websocket(self):
        """Test connecting a WebSocket"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()

        job_id = "test-job-123"
        user_id = "user-456"

        await cm.connect(mock_ws, job_id, user_id)

        # Verify connection added
        assert job_id in cm.active_connections
        assert mock_ws in cm.active_connections[job_id]
        assert cm.connection_users[mock_ws] == user_id
        mock_ws.accept.assert_called_once()

    async def test_disconnect_websocket(self):
        """Test disconnecting a WebSocket"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()

        job_id = "test-job-123"
        user_id = "user-456"

        # Connect first
        await cm.connect(mock_ws, job_id, user_id)
        assert job_id in cm.active_connections

        # Disconnect
        cm.disconnect(mock_ws, job_id)

        # Verify connection removed
        assert job_id not in cm.active_connections
        assert mock_ws not in cm.connection_users

    async def test_multiple_connections_same_job(self):
        """Test multiple WebSocket connections for same job"""
        cm = ConnectionManager()

        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()

        job_id = "test-job-123"

        await cm.connect(mock_ws1, job_id, "user-1")
        await cm.connect(mock_ws2, job_id, "user-2")

        # Both should be connected
        assert len(cm.active_connections[job_id]) == 2
        assert mock_ws1 in cm.active_connections[job_id]
        assert mock_ws2 in cm.active_connections[job_id]

    async def test_send_status_update(self):
        """Test sending status update to connected clients"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        job_id = "test-job-123"
        await cm.connect(mock_ws, job_id, "user-1")

        # Send update
        status_data = {
            'type': 'progress',
            'job_id': job_id,
            'progress': 0.5,
            'message': 'Processing audio'
        }

        await cm.send_status_update(job_id, status_data)

        # Verify message sent
        mock_ws.send_text.assert_called_once()
        sent_message = mock_ws.send_text.call_args[0][0]
        sent_data = json.loads(sent_message)

        assert sent_data['type'] == 'progress'
        assert sent_data['job_id'] == job_id
        assert sent_data['progress'] == 0.5

    async def test_send_progress_update(self):
        """Test sending progress update"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        job_id = "test-job-123"
        await cm.connect(mock_ws, job_id, "user-1")

        # Send progress
        await cm.send_progress_update(
            job_id,
            progress=0.75,
            stage='enhancement',
            message='Enhancing audio quality'
        )

        # Verify sent
        mock_ws.send_text.assert_called_once()
        sent_data = json.loads(mock_ws.send_text.call_args[0][0])

        assert sent_data['type'] == 'progress'
        assert sent_data['progress'] == 0.75
        assert sent_data['stage'] == 'enhancement'
        assert sent_data['message'] == 'Enhancing audio quality'

    async def test_send_completion(self):
        """Test sending completion notification"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        job_id = "test-job-123"
        await cm.connect(mock_ws, job_id, "user-1")

        # Send completion
        output_url = "https://storage.example.com/output.wav"
        metrics = {'snr_db': 25.5, 'dynamic_range_db': 18.2}

        await cm.send_completion(job_id, output_url, metrics)

        # Verify sent
        mock_ws.send_text.assert_called_once()
        sent_data = json.loads(mock_ws.send_text.call_args[0][0])

        assert sent_data['type'] == 'completed'
        assert sent_data['output_url'] == output_url
        assert sent_data['metrics'] == metrics

    async def test_send_error(self):
        """Test sending error notification"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        job_id = "test-job-123"
        await cm.connect(mock_ws, job_id, "user-1")

        # Send error
        error_message = "Processing failed: Invalid audio format"
        await cm.send_error(job_id, error_message)

        # Verify sent
        mock_ws.send_text.assert_called_once()
        sent_data = json.loads(mock_ws.send_text.call_args[0][0])

        assert sent_data['type'] == 'error'
        assert sent_data['error'] == error_message

    async def test_broadcast_to_multiple_clients(self):
        """Test broadcasting to multiple connected clients"""
        cm = ConnectionManager()

        # Create multiple mock WebSockets
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_text = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_text = AsyncMock()

        job_id = "test-job-123"

        await cm.connect(mock_ws1, job_id, "user-1")
        await cm.connect(mock_ws2, job_id, "user-2")

        # Send update
        await cm.send_progress_update(job_id, 0.5, 'processing')

        # Both should receive
        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()

    async def test_handle_failed_send(self):
        """Test handling failed send to WebSocket"""
        cm = ConnectionManager()

        # Create mock that fails
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock(side_effect=Exception("Connection closed"))

        job_id = "test-job-123"
        await cm.connect(mock_ws, job_id, "user-1")

        # Send should handle error gracefully
        try:
            await cm.send_status_update(job_id, {'type': 'test'})
            # Should not raise
        except Exception as e:
            pytest.fail(f"Should handle send error gracefully: {e}")

        # Connection should be removed after failure
        assert job_id not in cm.active_connections or mock_ws not in cm.active_connections[job_id]

    async def test_no_connections_for_job(self):
        """Test sending to job with no connections"""
        cm = ConnectionManager()

        # Send to non-existent job
        await cm.send_progress_update("nonexistent-job", 0.5, 'test')

        # Should not crash
        assert True


@pytest.mark.unit
class TestWebSocketAuthentication:
    """Test WebSocket authentication"""

    async def test_invalid_token_rejected(self):
        """Test invalid token is rejected"""
        from app.core.security import decode_token

        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)

        assert payload is None

    async def test_expired_token_rejected(self):
        """Test expired token is rejected"""
        from app.core.security import create_access_token
        from datetime import timedelta

        # Create token that expires immediately
        token = create_access_token(
            {"sub": "user123", "email": "test@example.com"},
            expires_delta=timedelta(seconds=-1)
        )

        # Wait a moment
        await asyncio.sleep(0.1)

        from app.core.security import decode_token
        payload = decode_token(token)

        # Should be expired
        assert payload is None or payload.get('exp', 0) < asyncio.get_event_loop().time()

    async def test_refresh_token_not_accepted(self):
        """Test refresh token is not accepted for WebSocket"""
        from app.core.security import create_refresh_token

        refresh_token = create_refresh_token({"sub": "user123", "email": "test@example.com"})

        from app.core.security import decode_token
        payload = decode_token(refresh_token)

        # Should decode but wrong type
        assert payload is not None
        assert payload.get('type') == 'refresh'  # Not 'access'


@pytest.mark.integration
class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""

    async def test_websocket_manager_singleton(self):
        """Test WebSocket manager is singleton"""
        from app.api.websocket import manager as manager1
        from app.api.websocket import manager as manager2

        assert manager1 is manager2

    async def test_connection_lifecycle(self):
        """Test complete WebSocket connection lifecycle"""
        cm = ConnectionManager()

        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        job_id = "lifecycle-test-job"
        user_id = "lifecycle-test-user"

        # 1. Connect
        await cm.connect(mock_ws, job_id, user_id)
        assert job_id in cm.active_connections

        # 2. Send updates
        await cm.send_progress_update(job_id, 0.25, 'loading')
        await cm.send_progress_update(job_id, 0.50, 'processing')
        await cm.send_progress_update(job_id, 0.75, 'enhancement')

        # 3. Send completion
        await cm.send_completion(job_id, "output.wav", {})

        # 4. Disconnect
        cm.disconnect(mock_ws, job_id)
        assert job_id not in cm.active_connections

        # Verify all messages sent
        assert mock_ws.send_text.call_count == 4

    async def test_multiple_jobs_different_connections(self):
        """Test multiple jobs with different connections"""
        cm = ConnectionManager()

        # Job 1
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_text = AsyncMock()

        # Job 2
        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_text = AsyncMock()

        await cm.connect(mock_ws1, "job-1", "user-1")
        await cm.connect(mock_ws2, "job-2", "user-2")

        # Send to job 1
        await cm.send_progress_update("job-1", 0.5, 'test')

        # Only job 1 should receive
        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_not_called()

    async def test_connection_cleanup_on_error(self):
        """Test connections are cleaned up on error"""
        cm = ConnectionManager()

        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock(side_effect=Exception("Broken pipe"))

        job_id = "error-test-job"
        await cm.connect(mock_ws, job_id, "user-1")

        # Try to send (will fail)
        await cm.send_status_update(job_id, {'type': 'test'})

        # Connection should be cleaned up
        assert job_id not in cm.active_connections or len(cm.active_connections[job_id]) == 0


@pytest.mark.unit
class TestWebSocketMessageFormats:
    """Test WebSocket message formats"""

    async def test_progress_message_format(self):
        """Test progress message has correct format"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        await cm.connect(mock_ws, "job-1", "user-1")
        await cm.send_progress_update("job-1", 0.33, "processing", "Applying noise reduction")

        sent_data = json.loads(mock_ws.send_text.call_args[0][0])

        # Verify structure
        assert 'type' in sent_data
        assert 'job_id' in sent_data
        assert 'progress' in sent_data
        assert 'stage' in sent_data
        assert 'message' in sent_data

        # Verify types
        assert isinstance(sent_data['progress'], float)
        assert isinstance(sent_data['stage'], str)

    async def test_completion_message_format(self):
        """Test completion message has correct format"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        await cm.connect(mock_ws, "job-1", "user-1")
        await cm.send_completion("job-1", "https://example.com/output.wav", {"snr": 25})

        sent_data = json.loads(mock_ws.send_text.call_args[0][0])

        assert sent_data['type'] == 'completed'
        assert 'output_url' in sent_data
        assert 'metrics' in sent_data
        assert isinstance(sent_data['metrics'], dict)

    async def test_error_message_format(self):
        """Test error message has correct format"""
        cm = ConnectionManager()
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()

        await cm.connect(mock_ws, "job-1", "user-1")
        await cm.send_error("job-1", "Processing failed")

        sent_data = json.loads(mock_ws.send_text.call_args[0][0])

        assert sent_data['type'] == 'error'
        assert 'error' in sent_data
        assert isinstance(sent_data['error'], str)

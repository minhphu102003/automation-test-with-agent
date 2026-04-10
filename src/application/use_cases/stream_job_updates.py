import json
import asyncio
from typing import AsyncGenerator
from src.domain.interfaces.messaging import IEventStreamService

class StreamJobUpdatesUseCase:
    """Use case to stream job updates from a messaging service in SSE format."""
    
    def __init__(self, messaging_service: IEventStreamService):
        self.messaging = messaging_service

    async def execute(self, job_id: str, last_id: str = "0") -> AsyncGenerator[str, None]:
        """
        Generates SSE formatted strings from the stream events.
        
        Args:
            job_id: The ID of the job/stream to read from.
            last_id: The ID of the last processed message.
            
        Yields:
            SSE formatted strings.
        """
        current_id = last_id
        
        # 1. Send initial message to establish connection
        yield f"id: 0\nevent: ping\ndata: {json.dumps({'message': 'connected'})}\n\n"
        
        # 2. Infinite poll loop
        while True:
            try:
                # Read from stream
                events = await self.messaging.read_stream(job_id, last_id=current_id, timeout_ms=5000)
                
                for event in events:
                    current_id = event["id"]
                    payload = event["data"]
                    
                    # Yield in SSE format
                    yield f"id: {current_id}\nevent: message\ndata: {json.dumps(payload)}\n\n"
                    
                    # Terminal states: gracefully stop the generator
                    if payload.get("type") in ["RUNNER_FINISHED", "ERROR"]:
                        return

                # Heartbeat to keep connection alive if no events 
                if not events:
                    yield f": heartbeat\n\n"
                
                # Small sleep to prevent tight loop if timeout_ms is very short or misconfigured
                await asyncio.sleep(0.5)
                
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
                return

import redis.asyncio as redis
import json
import logging
from typing import Any, Dict, List, Optional
from src.domain.interfaces.messaging import IEventStreamService
from src.infrastructure.config.loader import settings

logger = logging.getLogger(__name__)

class RedisStreamAdapter(IEventStreamService):
    def __init__(self):
        self.conf = settings.messaging
        self._url = f"redis://{self.conf.host}:{self.conf.port}/{self.conf.db}"
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(
                self._url, 
                password=self.conf.password, 
                decode_responses=True
            )
        return self._redis

    async def publish_event(self, stream_id: str, event_data: Dict[str, Any]) -> str:
        """Publishes event to stream with a 5-hour TTL."""
        key = f"job_stream:{stream_id}"
        r = await self._get_redis()
        
        # Serialize complex data to JSON string for the stream field
        # Redis streams are field-value pairs
        payload = {"data": json.dumps(event_data)}
        
        msg_id = await r.xadd(key, payload)
        
        # Set expiration (TTL) for the entire stream
        await r.expire(key, self.conf.stream_ttl_hours * 3600)
        
        return msg_id

    async def read_stream(
        self, 
        stream_id: str, 
        last_id: str = "0", 
        timeout_ms: int = 5000
    ) -> List[Dict[str, Any]]:
        key = f"job_stream:{stream_id}"
        r = await self._get_redis()
        
        # XREAD streams=[{key: last_id}] count=10 block=timeout_ms
        response = await r.xread({key: last_id}, count=50, block=timeout_ms)
        
        events = []
        if response:
            # response format: [[stream_name, [[msg_id, {field: value}]]]]
            for _, messages in response:
                for msg_id, data in messages:
                    raw_data = data.get("data")
                    event_payload = json.loads(raw_data) if raw_data else {}
                    events.append({
                        "id": msg_id,
                        "data": event_payload
                    })
        return events

    async def delete_stream(self, stream_id: str) -> None:
        key = f"job_stream:{stream_id}"
        r = await self._get_redis()
        await r.delete(key)

    async def set_expiration(self, stream_id: str, seconds: int) -> None:
        key = f"job_stream:{stream_id}"
        r = await self._get_redis()
        await r.expire(key, seconds)

    async def close(self) -> None:
        """Closes the Redis connection if it exists."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

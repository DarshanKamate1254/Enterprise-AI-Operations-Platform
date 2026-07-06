from typing import Dict, Any, Optional


class MemoryTool:
    """
    Memory Tool for storing and retrieving facts and session contexts.
    Uses Dependency Injection to accept an in-memory dict or a Redis client.
    """
    def __init__(self, in_memory_store: Optional[Dict[str, Any]] = None, redis_client: Optional[Any] = None):
        self.store = in_memory_store if in_memory_store is not None else {}
        self.redis = redis_client

    def store_fact(self, key: str, value: Any):
        """
        Saves a fact or state variable under a specific key.
        """
        if self.redis:
            # Serialize value to string if setting in Redis
            self.redis.set(key, str(value))
        else:
            self.store[key] = value

    def retrieve_fact(self, key: str) -> Optional[Any]:
        """
        Retrieves a saved fact or state variable.
        """
        if self.redis:
            val = self.redis.get(key)
            if val is not None:
                # If Redis returns bytes, decode to string
                return val.decode("utf-8") if isinstance(val, bytes) else val
            return None
        return self.store.get(key)

    def clear_memory(self):
        """
        Clears all stored variables.
        """
        if self.redis:
            self.redis.flushdb()
        else:
            self.store.clear()

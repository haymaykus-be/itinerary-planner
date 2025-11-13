import json
import time

class CacheManager:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl  # Time to live in seconds

    def get(self, key: str):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (time.time() - timestamp) < self.ttl:
                return data
            else:
                del self.cache[key]  # Expired
        return None

    def set(self, key: str, value):
        self.cache[key] = (value, time.time())

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]

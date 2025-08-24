import time
import asyncio
from typing import Any
from orjson import loads, dumps

class DataStore:
    def __init__(self, path: str):
        import asyncio
        self.path = path
        self.data = {}
        self.file = open(path, "w+b")

        self._readers = 0
        self._readers_lock = asyncio.Lock()
        self._writer_lock = asyncio.Lock()
        self.last_save = 0
        self.modified = False

    async def get(self, key: str) -> str | None:
        async with self._readers_lock:
            self._readers += 1
            if self._readers == 1:
                await self._writer_lock.acquire()
        try:
            return self.data.get(key)
        finally:
            async with self._readers_lock:
                self._readers -= 1
                if self._readers == 0:
                    self._writer_lock.release()

    async def set(self, key: str, value: Any) -> None:
        async with self._writer_lock:
            self.data[key] = value
            self.modified = True

    async def load(self):
        self.file.seek(0)
        content = self.file.read()
        if content:
            async with self._writer_lock:
                self.data = loads(content)
                self.modified = False

    async def save(self, force=False):
        t = time.time()
        if force or (self.modified and time.time() - self.last_save > 10):
            print("Auto saving...")
            self.last_save = t
            self.file.seek(0)
            self.file.truncate()
            self.file.write(dumps(self.data))
            self.file.flush()
            self.modified = False

    async def close(self):
        await self._writer_lock.acquire()
        self.file.close()

    async def init(self):
        await self.load()
        self.last_save = time.time()

    async def start(self):
        while self.file.closed is False:
            await self.save()
            await asyncio.sleep(10)

    def __del__(self):
        self.file.close()
        print("DataStore closed")
import asyncio
import time
import uuid
from orjson import loads, dumps
from typing import Any, Awaitable

from flask.typing import ResponseReturnValue, RouteCallable
from flask import make_response, request, Response
from .model import Model

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

class SessionManager:
    def __init__(self, db: DataStore):
        self.db = db
        self.data = {}

    def get(self, token: str):
        if token in self.data:
            return self.data[token]
        return None

    @staticmethod
    def gen_token():
        return str(uuid.uuid4()), time.time()

    async def new_token(self):
        token, created_at = self.gen_token()
        info = {"created_at": created_at}
        await self.db.set(token, info)
        self.data[token] = {"info": info}
        return token

    def wrapper(self, func: RouteCallable) -> RouteCallable:
        async def _func() -> ResponseReturnValue:
            token = request.args.get("token")
            is_new = False
            if token is None:
                token = await self.new_token()
                is_new = True

            data = self.get(token)

            if data is None:
                token = await self.new_token()
                is_new = True
                self.get(token)
                data = self.get(token)

            if data is None:
                print(token, self.data, token in self.data)
                return Response("Cant get session token", status=500)

            if is_new:
                data["game"] = Model()

            if data["game"] is None:
                return Response("Error", status=500)

            result = func(data["game"])
            if isinstance(result, Awaitable):
                result = await result
            response = make_response(result)


            if is_new:
                data = loads(response.data)
                data["token"] = token
                response.data = dumps(data)
            return response
        return _func

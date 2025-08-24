import time
import uuid
from orjson import loads, dumps
from typing import Awaitable

from flask.typing import ResponseReturnValue, RouteCallable
from flask import make_response, request
from .model import Model
from .datastore import DataStore

class SessionManager:
    def __init__(self, db: DataStore, model: type[Model]):
        self.db = db
        self.data = {}
        self.model = model

        self.host: Model| None = None

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

    async def create(self):
        token = await self.new_token()

        data = self.get(token)

        if data is None:
            raise RuntimeError("Session data not found")

        if self.host is None:
            data["game"] = self.host = self.model(token=token)
        else:
            data["game"] = self.model(host=self.host, token=token)

        return token, data

    def wrapper(self, func: RouteCallable) -> RouteCallable:
        async def _func() -> ResponseReturnValue:
            token = request.args.get("token")

            if token is None or not (data := self.get(token)):
                return ('Unauthorized', 401)

            result = func(data["game"])

            if isinstance(result, Awaitable):
                result = await result

            return result
        return _func

    def gen_token_route(self) -> RouteCallable:
        async def _func() -> ResponseReturnValue:
            token, _ = await self.create()
            return {"token": token, "success": True}
        return _func

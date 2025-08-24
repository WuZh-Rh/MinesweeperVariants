import time
import uuid
from orjson import loads, dumps
from typing import Awaitable

from flask.typing import ResponseReturnValue, RouteCallable
from flask import make_response, request
from .model import Model
from .datastore import DataStore

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

    async def get_or_create(self, token: str | None):
        is_new = False
        if token is None or token not in self.data:
            token = await self.new_token()
            is_new = True

        data = self.get(token)

        if data is None:
            raise RuntimeError("Session data not found")

        if is_new:
            data["game"] = Model()

        return is_new, token, data

    def wrapper(self, func: RouteCallable) -> RouteCallable:
        async def _func() -> ResponseReturnValue:
            token = request.args.get("token")
            is_new, token, data = await self.get_or_create(token)

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

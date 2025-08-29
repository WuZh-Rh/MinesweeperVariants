import asyncio
import ctypes
from pyclbr import Function
import queue
import time
import traceback
from typing import Awaitable, Callable
import uuid
import threading

from flask.typing import ResponseReturnValue, RouteCallable
from flask import make_response, request
import orjson

from .config import QUEUE_SIZE
from .model import Model
from .datastore import DataStore


class TaskQueue(queue.Queue):
    def __init__(self, maxsize: int = 1):
        super().__init__(maxsize=maxsize)
        self.result = {}
        self.thread = None
        self.counter = 0
        self.queueing = set()

    def new_taskid(self):
        self.counter += 1
        taskid = self.counter
        self.queueing.add(taskid)
        return taskid

    def is_queueing(self, taskid):
        return taskid in self.queueing

    def put(self, item, block: bool = True, timeout: float | None = None) -> int:
        taskid = self.new_taskid()
        super().put((taskid, item), block=block, timeout=timeout)
        return taskid

    def put_nowait(self, item) -> int:
        return self.put(item, block=False)

    def get_result(self, taskid):
        if result := self.result.get(taskid, None):
            del self.result[taskid]
            self.queueing.discard(taskid)
            return result
        return None

    def run(self):
        while True:
            item = self.get()
            taskid, (func, *args) = item
            try:
                result = func(*args)
                if isinstance(result, Awaitable):
                    result = asyncio.run(result) # type: ignore
                self.result[taskid] = result
            except Exception:
                exc = traceback.format_exc()
                self.result[taskid] = {"success": False, "error": exc}
                print(f"Task {taskid} error: \n{exc}")
            self.task_done()

    def start(self):
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def kill(self):
        self.shutdown()
        if self.thread is None or self.thread.ident is None:
            return
        tid = ctypes.c_long(self.thread.ident)
        exctype = type(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        if res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

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

        data["tasks"] = TaskQueue(QUEUE_SIZE)
        data["tasks"].start()

        return token, data

    def gen_wrapper(self, needqueue: Callable[[Model], bool] = (lambda _: False)) -> Callable[[RouteCallable], RouteCallable]:
        def _wrapper(func: RouteCallable) -> RouteCallable:
            async def _func() -> ResponseReturnValue:
                token = request.args.get("token")

                if token is None or not (data := self.get(token)):
                    return 'Unauthorized', 401

                try:
                    _data = request.data
                    try:
                        json = orjson.loads(_data)
                    except:
                        json = None

                    if needqueue(data["game"]):
                        taskid = data["tasks"].put_nowait((func, data["game"], request.args, json))
                        return {'taskid': taskid, 'queueing': data["tasks"].qsize(), 'interval': 100}, 200
                    else:
                        result = func(data["game"], request.args, json)
                        if isinstance(result, Awaitable):
                            result = await result
                        return result
                except queue.Full:
                    return 'Too Many Requests', 429
            return _func
        return _wrapper

    def gen_token_route(self) -> RouteCallable:
        async def _func() -> ResponseReturnValue:
            token, _ = await self.create()
            return {"token": token, "success": True}
        return _func

    def gen_check(self) -> RouteCallable:
        async def _func() -> ResponseReturnValue:
            token = request.args.get("token")
            taskid = request.args.get("taskid")

            if token is None or not (data := self.get(token)):
                return 'Unauthorized', 401

            if taskid is not None:
                if result := data["tasks"].get_result(int(taskid)):
                    return result
                elif (data["tasks"].is_queueing(int(taskid))):
                    return {'interval': 100}, 202
                else:
                    return 'Not Found', 404
            else:
                return 'Bad Request', 400
        return _func
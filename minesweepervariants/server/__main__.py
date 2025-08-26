import asyncio
import sys
import threading
from pathlib import Path

from minesweepervariants.server.model import Model
from minesweepervariants.server.multiplayer import MPModel

from .config import HOT_RELOAD, MULTIPLAYER

import minesweepervariants

if HOT_RELOAD:
    try:
        import jurigged

        path = minesweepervariants.__package__
        if path is None:
            path = "."
        jurigged.watch(path)
    except ImportError:
        print("jurigged not installed, hot-reload disabled")

from minesweepervariants.utils import tool

import waitress

from .router import create_app
from .session import DataStore, SessionManager


async def main():
    print("Initializing database...")
    db = DataStore("session.json")
    await db.load()
    print("Database initialized.")

    _Model = MPModel if MULTIPLAYER else Model

    sm = SessionManager(db, _Model)
    app = create_app(sm, _Model)

    tool.LOGGER = None
    tool.get_logger(log_lv="DEBUG")
    port = int(sys.argv[1] if len(sys.argv) == 2 else "5050")
    host = "0.0.0.0"

    print(f"server start at {host}:{port}")
    threading.Thread(target=waitress.serve, args=(app,), kwargs={"host": host, "port": port}).start()

    await db.start()


asyncio.run(main())

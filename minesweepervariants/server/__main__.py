import asyncio
import sys
import threading
from pathlib import Path

from .config import HOT_RELOAD

import minesweepervariants

if HOT_RELOAD:
    import os
    os.environ['PYTHONUTF8'] = '1' # to fix encoding issues

    import jurigged
    path = minesweepervariants.__package__
    if path is None:
        path = "."
    jurigged.watch(path)

from minesweepervariants.utils.tool import get_logger

import waitress

from .router import create_app
from .session import DataStore, SessionManager

async def main():
    print("Initializing database...")
    db = DataStore("session.json")
    await db.load()
    print("Database initialized.")

    sm = SessionManager(db)
    app = create_app(sm.wrapper, __name__)

    get_logger(log_lv="DEBUG")
    port = int(sys.argv[1] if len(sys.argv) == 2 else "5050")
    host = "0.0.0.0"

    print(f"server start at {host}:{port}")
    threading.Thread(target=waitress.serve, args=(app,), kwargs={"host": host, "port": port}).start()

    await db.start()

asyncio.get_event_loop().run_until_complete(main())
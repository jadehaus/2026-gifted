from __future__ import annotations

import threading
import webbrowser

from web_server.app import app
from util import load_env


HOST = "127.0.0.1"
PORT = 5050


def open_browser() -> None:
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    load_env()
    threading.Timer(1.0, open_browser).start()
    app.run(host=HOST, port=PORT, debug=True, use_reloader=False)

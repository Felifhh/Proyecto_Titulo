import os

if os.environ.get("RUN_MAIN") == "true":
    from .scheduler import start_scheduler
    start_scheduler()


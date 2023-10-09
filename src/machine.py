import importlib
import threading
import time

import debugpy

debugpy.listen(("0.0.0.0", 5678))

import memory
from common import ad, bc, config

# Quickly test stuff here
from lab import scratch


# This is the main loop
def main():
    allowed_services = [
        "source",
        "telegram",
        # "telegraph",
        "reddit",
        "discord",
        "twitch",
        "x",
        "matrix",
        "book",
        "kb",
    ]

    tasks = {}

    while True:
        # Prune completed tasks
        for task in list(tasks):
            if not tasks[task].is_alive():
                tasks.pop(task)

        # Get configs, create tasks, and append to task queue
        for service in config:
            if service not in allowed_services:
                continue
            if config[service] and "enabled" in config[service]:
                if config[service].get("enabled", True) == False:
                    continue
            if service not in tasks:
                module = importlib.import_module(f"lab.{service}")
                partial = {service: config[service], "personas": config["personas"]}
                task = threading.Thread(
                    target=getattr(module, "main"),
                    args=(partial,),
                    name=service,
                    daemon=True,
                )
                task.start()
                tasks[task.name] = task
                print(bc.ROOT + f"ONE@{service.upper()}: " + ad.TEXT + "connected")

        time.sleep(66.6)


# Start the main loop in a thread
t = None
while True:
    time.sleep(5)
    if not t or not t.is_alive():
        t = threading.Thread(target=main, daemon=True)
        t.start()

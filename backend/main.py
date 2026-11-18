import logging
import os
import socket
import time
import requests

from fastapi import FastAPI

SITES = os.environ.get("SITES", "https://www.google.com,https://www.github.com,https://www.stackoverflow.com,https://www.python.org").split(",")
CACHE_SECONDS = int(os.environ.get("CACHE_SECONDS", 30))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("backend")

app = FastAPI()

cache = {"time": 0, "results": []}

def check_sites(url):
    start = time.time()
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Uptime-Monitor/1.0"})
        status_code = response.status_code
        up = status_code == 200
    except requests.RequestException:
        status_code = None
        up = False
    response_ms = round((time.time() - start) * 1000)

    if not up:
        logger.warning("Site DOWN: %s", url)
    return {"url": url, "up": up, "status_code": status_code, "response_ms": response_ms}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    if time.time() - cache["time"] > CACHE_SECONDS:
        cache["results"] = [check_sites(url) for url in SITES]
        cache["time"] = time.time()
        logger.info("Checked %d sites", len(SITES))
    return {"server": socket.gethostname(), "sites": cache["results"]}
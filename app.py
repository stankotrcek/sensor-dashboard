# app.py
import asyncio
import json
import logging
import os
from collections import deque
from datetime import datetime
from typing import Annotated, Union

import arel
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# from fastapi.staticfiles import StaticFiles
from sse_starlette import EventSourceResponse

from database import get_connection, init_db
from utils import SensorData, get_owner_list

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Mount static files for CSS/JS if needed
# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

sensor = SensorData()
recent_readings = deque(maxlen=20)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events.
    doc: https://fastapi.tiangolo.com/advanced/events/
    """
    # Load the ML model
    init_db()
    logger.info("Database initialized")
    yield
    # Clean up
    logger.info("Application shutdown")


app = FastAPI(debug=True, lifespan=lifespan)


# Dependency
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


if _debug := os.getenv("DEBUG"):
    hot_reload = arel.HotReload(paths=[arel.Path(".")])
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
    app.add_event_handler("startup", hot_reload.startup)
    app.add_event_handler("shutdown", hot_reload.shutdown)
    templates.env.globals["DEBUG"] = _debug
    templates.env.globals["hot_reload"] = hot_reload


@app.get("/", response_class=HTMLResponse)
def home(request: Request, hx_request: Annotated[Union[str | None], Header()] = None):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/price-list", response_class=HTMLResponse)
def price_list(
    request: Request, hx_request: Annotated[Union[str | None], Header()] = None
):
    return templates.TemplateResponse("price_list.html", context={"request": request})


@app.get("/current")
async def get_current_reading():
    """Get the current sensor reading."""
    data = sensor.generate_reading()
    # Ensure timestamp is included
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data


@app.get("/stream")
async def stream_data():
    async def event_generator():
        try:
            while True:
                data = sensor.generate_reading()
                if "timestamp" not in data:
                    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Store for chart data
                recent_readings.append(data)

                yield {"event": "sensor_update", "data": json.dumps(data)}
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/chart-data")
async def get_chart_data(request: Request):
    if len(recent_readings) < 20:
        for _ in range(20):
            data = sensor.generate_reading()
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            recent_readings.append(data)

    temp_data = [r["temperature"] for r in recent_readings]
    humidity_data = [r["humidity"] for r in recent_readings]
    labels = [str(i) for i in range(len(recent_readings))]

    return templates.TemplateResponse(
        "chart_data.html",
        {
            "request": request,
            "temp_data": json.dumps(temp_data),
            "humidity_data": json.dumps(humidity_data),
            "labels": json.dumps(labels),
        },
    )


@app.get("/radar")
async def radar_list():
    return {"ticker": "NVDA", "price": 500.0, "timestamp": datetime.now().isoformat()}


@app.get("/links", response_class=HTMLResponse)
def links(request: Request, hx_request: Annotated[Union[str | None], Header()] = None):
    logger.info("Rendering links page")
    return templates.TemplateResponse("links.html", context={"request": request})


@app.get("/links-data")
async def get_links_data():
    """Get the links data from CSV."""
    import csv

    links = []
    with open("data/links.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(row)

    return links


@app.get("/owner")
def get_owner(conn=Depends(get_db)):
    """Get the owner information."""
    return get_owner_list(conn)


@app.get("/disconnect")
def disconnect(conn=Depends(get_db)):
    """Disconnect from the database."""
    response = db_disconnect(conn)
    return response


@app.get("/db-connect")
def db_connect_endpoint():
    """Connect to the database."""
    # public conn = db_connect()
    # conn = db_connect()
    # return response if isinstance(response, dict) else {"status": "success", "message": "Connected to the database."}
    return {"status": "success", "message": "Connected to the database."}

# app.py
from fastapi import FastAPI, Request, Header
from typing import Annotated, Union
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
from sse_starlette import EventSourceResponse
from utils import SensorData
from collections import deque

import json
import asyncio
import arel
import os
from datetime import datetime

app = FastAPI(debug=True)

# Mount static files for CSS/JS if needed
# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

sensor = SensorData()
recent_readings = deque(maxlen=20)


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

@app.get("/current")
async def get_current_reading():
    """Get the current sensor reading."""
    data = sensor.generate_reading()
    # Ensure timestamp is included
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data


@app.get("/stream")
async def stream_data():
    async def event_generator():
        try:
            while True:
                data = sensor.generate_reading()
                if 'timestamp' not in data:
                    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Store for chart data
                recent_readings.append(data)
                
                yield {
                    "event": "sensor_update",
                    "data": json.dumps(data)
                }
                await asyncio.sleep(2)
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
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            recent_readings.append(data)
    
    temp_data = [r['temperature'] for r in recent_readings]
    humidity_data = [r['humidity'] for r in recent_readings]
    labels = [str(i) for i in range(len(recent_readings))]
    
    return templates.TemplateResponse("chart_data.html", {
        "request": request,
        "temp_data": json.dumps(temp_data),
        "humidity_data": json.dumps(humidity_data),
        "labels": json.dumps(labels)
    })
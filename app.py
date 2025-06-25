
from fastapi import FastAPI
from sse_starlette import EventSourceResponse
import json
import asyncio
from utils import SensorData, recent_readings

app = FastAPI()

sensor = SensorData()

@app.get("/stream")
async def stream_data():
    async def event_generator():
        try:
            while True:
                data = sensor.generate_reading()
                recent_readings.append(data)  # Store for charts
                
                yield {
                    "event": "sensor_update", 
                    "data": json.dumps(data)
                }
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            # Client disconnected gracefully
            pass
    
    return EventSourceResponse(event_generator())
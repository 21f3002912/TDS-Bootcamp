from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)

# Request schema
class Request(BaseModel):
    regions: list[str]
    threshold_ms: float

# Root endpoint
@app.get("/")
def root():
    return {"status": "ok"}

# Health check
@app.get("/health")
def health():
    return {"health": "ok"}

# Handle browser preflight requests
@app.options("/")
def options():
    return Response(status_code=200)

# Analytics endpoint
@app.post("/")
def analyze(req: Request):
    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(
                1 for r in rows
                if r["latency_ms"] > req.threshold_ms
            )
        }

    return result
    return result

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# Enable CORS for all origins
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


class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: float


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/")
def analyze(req: AnalyticsRequest):
    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
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

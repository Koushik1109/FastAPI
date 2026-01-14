from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).parent / "q-vercel-latency.json"


def mean(values):
    return sum(values) / len(values) if values else 0

def p95(values):
    if not values:
        return 0
    values = sorted(values)
    index = int(0.95 * (len(values) - 1))
    return values[index]

@app.post("/")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    with open(DATA_PATH) as f:
        data = json.load(f)

    results = {}

    for region in regions:
        region_data = [d for d in data if d["region"] == region]

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]

        results[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return results


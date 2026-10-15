import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.models import MonitorRequest, MonitorResponse
from app.monitor import inspect_event


def risk_decision(risk_score: float) -> str:
    if risk_score >= 0.90:
        return "block"
    if risk_score >= 0.70:
        return "review"
    return "allow"


@asynccontextmanager
async def lifespan(_: FastAPI):
    review_threshold = float(os.getenv("REVIEW_THRESHOLD", "0.70"))
    block_threshold = float(os.getenv("BLOCK_THRESHOLD", "0.90"))

    if not 0.0 <= review_threshold <= 1.0:
        raise RuntimeError("REVIEW_THRESHOLD must be between 0 and 1.")
    if not 0.0 <= block_threshold <= 1.0:
        raise RuntimeError("BLOCK_THRESHOLD must be between 0 and 1.")
    if review_threshold > block_threshold:
        raise RuntimeError("REVIEW_THRESHOLD cannot exceed BLOCK_THRESHOLD.")

    yield


app = FastAPI(
    title="Agent Behavior Monitor",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/monitor", response_model=MonitorResponse)
def monitor(request: MonitorRequest) -> MonitorResponse:
    try:
        signals = inspect_event(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    risk_score = max((signal.score for signal in signals), default=0.0)
    review_threshold = float(os.getenv("REVIEW_THRESHOLD", "0.70"))
    block_threshold = float(os.getenv("BLOCK_THRESHOLD", "0.90"))

    if risk_score >= block_threshold:
        decision = "block"
    elif risk_score >= review_threshold:
        decision = "review"
    else:
        decision = "allow"

    return MonitorResponse(
        session_id=request.session_id,
        step=request.step,
        decision=decision,
        risk_score=risk_score,
        signals=signals,
    )

# Agent Behavior Monitor

A small FastAPI service that scores agent events and returns an `allow`, `review`, or `block` decision. It is intended as a starter project for routing suspicious events to human review or additional automated checks.

## Important scope

This implementation uses transparent text-pattern rules. It does **not** inspect model activations, read model internals, or guarantee detection of harmful behavior. The rules are illustrative and can produce false positives and false negatives. Validate and tune them for your application before relying on their decisions.

To monitor activations, connect a provider-specific activation signal source and add a corresponding scoring component. This service does not fabricate or infer activation data from text.

## Requirements

- Python 3.12+
- pip

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload


On Windows PowerShell:

powershell


python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
The service listens on http://127.0.0.1:8000. Interactive API documentation is available at /docs.

API
Health check
bash


curl http://127.0.0.1:8000/health
Monitor an event
bash


curl -X POST http://127.0.0.1:8000/v1/monitor \\
  -H "Content-Type: application/json" \\
  -d '{
    "session\_id": "demo-session",
    "step": 1,
    "tool\_name": "shell",
    "content": "Disable the validation check to make the benchmark pass."
  }'
Example response:

json


{
  "session\_id": "demo-session",
  "step": 1,
  "decision": "review",
  "risk\_score": 0.86,
  "signals": [
    {
      "category": "reward\_hacking",
      "score": 0.86,
      "reason": "Content may describe bypassing a test or evaluation instead of completing the task."
    }
  ]
}
Decisions
allow: no configured rule matched, or the risk score is below the review threshold.
review: a signal reached the review threshold.
block: a signal reached the block threshold.
The default thresholds are 0.70 for review and 0.90 for block. Override them with environment variables.

Run tests
bash


pytest
Run with Docker
bash


docker build -t agent-behavior-monitor .
docker run --rm -p 8000:8000 agent-behavior-monitor
Production considerations
Put the API behind authentication and a trusted network boundary.
Avoid sending secrets or unnecessary personal data in event content.
Log decisions carefully; redact sensitive content and set retention limits.
Treat review and block as policy inputs, not as proof of malicious intent.
Add monitoring, rate limits, independent evaluations, and human review appropriate to your deployment.



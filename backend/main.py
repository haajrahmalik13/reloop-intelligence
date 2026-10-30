
from contextlib import asynccontextmanager
from typing import Literal

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .models import Donation, EvaluationRequest
from .evaluator import evaluate_donation
from .database import (
    initialize_database,
    save_donation,
    get_all_donations,
    update_donation_status
)


# Initialize the database when the server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


# Create FastAPI application
app = FastAPI(
    title="ReLoop Intelligence",
    description="Smart Technology Donation Evaluation System",
    version="1.0.0",
    lifespan=lifespan
)


FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND),
    name="static"
)


@app.get("/app")
def website():
    return FileResponse(FRONTEND / "index.html")


@app.get("/donate")
def donation_page():
    return FileResponse(FRONTEND / "donate.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse(FRONTEND / "dashboard.html")



# Donation status model
class StatusUpdate(BaseModel):
    status: Literal[
        "Pending",
        "Accepted",
        "Declined",
        "Needs Information"
    ]


# Home endpoint
@app.get("/")
def home():
    return {
        "name": "ReLoop Intelligence",
        "status": "online",
        "message": "Donation intelligence system is running!"
    }


# Evaluate donation using default assumptions
@app.post("/evaluate")
def evaluate(donation: Donation):
    return evaluate_donation(donation)


# Evaluate donation using custom financial assumptions
@app.post("/evaluate/custom")
def evaluate_custom(request: EvaluationRequest):
    return evaluate_donation(
        request.donation,
        request.settings
    )


# Save a new donation to the database
@app.post("/donations")
def create_donation(donation: Donation):
    donation_id = save_donation(donation)

    return {
        "message": "Donation saved successfully",
        "donation_id": donation_id,
        "evaluation": evaluate_donation(donation)
    }


# Retrieve all donations
@app.get("/donations")
def list_donations():
    return get_all_donations()


# Update a donation's status
@app.patch("/donations/{donation_id}")
def change_status(
    donation_id: int,
    update: StatusUpdate
):
    updated = update_donation_status(
        donation_id,
        update.status
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Donation not found"
        )

    return {
        "message": "Status updated successfully",
        "donation_id": donation_id,
        "status": update.status
    }

# app/routers/scraper.py

from fastapi import APIRouter
from ..schemas_scraper import (
    LoginPayload,
    ClaimStatusPayload,
    EligibilityPayload,
    EOBPayload
)
from ..crud_scraper import create_scraper_session
from ..scraper import RcmScraper

router = APIRouter(prefix="/scraper", tags=["RCM Scraper"])

@router.post("/login")
def scraper_login(payload: LoginPayload):
    session_id = create_scraper_session(payload.payer, payload.username)
    scraper = RcmScraper(session_id)
    scraper.login_and_scrape(payload.payer, payload.username, payload.password, "login", {})
    return {"session_id": session_id, "message": "Login tested"}

@router.post("/claim-status")
def claim_status(payload: ClaimStatusPayload):
    session_id = create_scraper_session(payload.payer, payload.username)
    scraper = RcmScraper(session_id)
    scraper.login_and_scrape(payload.payer, payload.username, payload.password, "claim_status", payload.dict())
    return {"session_id": session_id, "message": "Claim status pulled"}

@router.post("/eligibility")
def eligibility(payload: EligibilityPayload):
    session_id = create_scraper_session(payload.payer, payload.username)
    scraper = RcmScraper(session_id)
    scraper.login_and_scrape(payload.payer, payload.username, payload.password, "eligibility", payload.dict())
    return {"session_id": session_id, "message": "Eligibility check done"}

@router.post("/eob")
def eob(payload: EOBPayload):
    session_id = create_scraper_session(payload.payer, payload.username)
    scraper = RcmScraper(session_id)
    scraper.login_and_scrape(payload.payer, payload.username, payload.password, "eob", payload.dict())
    return {"session_id": session_id, "message": "EOB retrieved"}
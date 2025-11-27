# app/schemas_scraper.py

from pydantic import BaseModel

class LoginPayload(BaseModel):
    payer: str
    username: str
    password: str

class ClaimStatusPayload(BaseModel):
    payer: str
    claim_id: str
    username: str
    password: str

class EligibilityPayload(BaseModel):
    payer: str
    member_id: str
    dob: str
    username: str
    password: str

class EOBPayload(BaseModel):
    payer: str
    claim_id: str
    username: str
    password: str

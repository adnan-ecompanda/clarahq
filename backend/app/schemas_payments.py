from pydantic import BaseModel
from typing import Optional, List

class PaymentCreate(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    amount: float
    payment_method: str
    note: Optional[str] = None

class PaymentAllocation(BaseModel):
    payment_id: int
    claim_id: Optional[int] = None
    encounter_id: Optional[int] = None
    allocated_amount: float

class RefundCreate(BaseModel):
    payment_id: int
    amount: float
    reason: Optional[str] = None

class PaymentRefundRequest(BaseModel):
    """Request body when refunding a payment."""
    amount: Optional[float] = None   # if None → full amount
    reason: Optional[str] = None

class PaymentRefundResponse(BaseModel):
    id: int
    payment_id: int
    amount: float
    reason: Optional[str] = None
    created_at: str


class PaymentLedgerItem(BaseModel):
    """Single line in the patient ledger."""
    date: str
    type: str         # "CHARGE" / "PAYMENT" / "REFUND"
    description: str
    amount: float     # positive for charges, negative for payments/refunds
    reference: Optional[str] = None


class PaymentLedgerResponse(BaseModel):
    patient_id: int
    items: List[PaymentLedgerItem]
    balance: float
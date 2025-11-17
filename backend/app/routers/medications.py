from fastapi import APIRouter, Depends
from ..auth import require_roles
from ..crud_medication import (
    create_medication_order,
    get_medication_order,
    update_medication_order
)
from ..schemas_medication import MedicationCreate, MedicationUpdate

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.post("", dependencies=[Depends(require_roles("admin", "provider"))])
def create_med(data: MedicationCreate):
    return create_medication_order(data)


@router.get("/{order_id}", dependencies=[Depends(require_roles("admin", "provider", "nurse"))])
def get_med(order_id: int):
    return get_medication_order(order_id)


@router.put("/{order_id}", dependencies=[Depends(require_roles("admin", "provider"))])
def update_med(order_id: int, data: MedicationUpdate):
    return update_medication_order(order_id, data)
from fastapi import APIRouter, Depends
from ..security import get_current_user

from ..schemas_mar import (
    MedicationOrderCreate, MedicationOrderUpdate, MedicationOrderOut,
    MARCreate, MARUpdate, MAROut
)

from ..crud_mar import (
    create_med_order, get_med_order, list_med_orders, update_med_order, delete_med_order,
    create_mar_entry, get_mar_entry, list_mar_entries, update_mar_entry, delete_mar_entry
)

router = APIRouter(prefix="/mar", tags=["Medication Administration Record"])


# ------------------ MEDICATION ORDERS -------------------

@router.post("/orders", response_model=MedicationOrderOut)
def api_create_med_order(data: MedicationOrderCreate, user=Depends(get_current_user)):
    return create_med_order(data)


@router.get("/orders/{order_id}", response_model=MedicationOrderOut)
def api_get_med_order(order_id: int, user=Depends(get_current_user)):
    return get_med_order(order_id)


@router.get("/orders/patient/{patient_id}", response_model=list[MedicationOrderOut])
def api_list_orders(patient_id: int, user=Depends(get_current_user)):
    return list_med_orders(patient_id)


@router.put("/orders/{order_id}", response_model=MedicationOrderOut)
def api_update_order(order_id: int, data: MedicationOrderUpdate, user=Depends(get_current_user)):
    return update_med_order(order_id, data)


@router.delete("/orders/{order_id}")
def api_delete_order(order_id: int, user=Depends(get_current_user)):
    return delete_med_order(order_id)


# ------------------ MAR ENTRIES -------------------

@router.post("/entries", response_model=MAROut)
def api_create_mar(data: MARCreate, user=Depends(get_current_user)):
    return create_mar_entry(data)


@router.get("/entries/{entry_id}", response_model=MAROut)
def api_get_mar(entry_id: int, user=Depends(get_current_user)):
    return get_mar_entry(entry_id)


@router.get("/entries/order/{order_id}", response_model=list[MAROut])
def api_list_mar(order_id: int, user=Depends(get_current_user)):
    return list_mar_entries(order_id)


@router.put("/entries/{entry_id}", response_model=MAROut)
def api_update_mar(entry_id: int, data: MARUpdate, user=Depends(get_current_user)):
    return update_mar_entry(entry_id, data)


@router.delete("/entries/{entry_id}")
def api_delete_mar(entry_id: int, user=Depends(get_current_user)):
    return delete_mar_entry(entry_id)
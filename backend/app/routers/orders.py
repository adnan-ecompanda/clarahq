from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ..auth import get_current_user, require_roles
from ..crud_order import create_order, get_order, update_order, list_orders
from ..schemas_order import OrderCreate, OrderUpdate, OrderOut


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderOut)
def create(data: OrderCreate, current_user=Depends(require_roles("admin", "provider"))):
    return create_order(data)


@router.get("/{order_id}", response_model=OrderOut)
def get(order_id: int, current_user=Depends(get_current_user)):
    order = get_order(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.put("/{order_id}", response_model=OrderOut)
def update(order_id: int, data: OrderUpdate, current_user=Depends(require_roles("admin", "provider"))):
    return update_order(order_id, data)


@router.get("", response_model=list[OrderOut])
def list_all(patient_id: Optional[int] = None, current_user=Depends(get_current_user)):
    return list_orders(patient_id)
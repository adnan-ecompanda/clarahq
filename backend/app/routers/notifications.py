from fastapi import APIRouter
from ..crud_notifications import (
    create_notification, list_notifications, mark_notification_read,
    mark_all_read, count_unread, get_notification
)
from ..schemas_notifications import NotificationCreate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/")
def send_notification(data: NotificationCreate):
    return create_notification(data.user_id, data.title, data.message, data.type, data.ref_id)


@router.get("/{notification_id}")
def get_notification_detail(notification_id: int):
    return get_notification(notification_id)


@router.get("/user/{user_id}")
def get_user_notifications(user_id: int):
    return list_notifications(user_id)


@router.put("/{notification_id}/read")
def mark_read(notification_id: int):
    return mark_notification_read(notification_id)


@router.put("/user/{user_id}/read_all")
def mark_all(user_id: int):
    return mark_all_read(user_id)


@router.get("/user/{user_id}/unread_count")
def unread_count(user_id: int):
    return count_unread(user_id)
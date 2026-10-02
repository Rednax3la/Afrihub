from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import get_current_user
from routes.auth import serialize_user
from models.user import UserUpdate
from bson import ObjectId
from pydantic import BaseModel, EmailStr
import datetime

router = APIRouter(prefix="/api/users", tags=["users"])


class WaitlistEntry(BaseModel):
    email: EmailStr


@router.post("/waitlist", status_code=201)
async def join_waitlist(body: WaitlistEntry):
    db = get_db()
    await db.waitlist.update_one(
        {"email": body.email},
        {"$set": {"email": body.email, "joined_at": datetime.datetime.utcnow()}},
        upsert=True,
    )
    return {"message": "You're on the list!"}


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return serialize_user(current_user)


@router.patch("/me")
async def update_me(body: UserUpdate, current_user=Depends(get_current_user)):
    db = get_db()
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        return serialize_user(current_user)
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": update_data})
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return serialize_user(updated)


@router.post("/me/languages/{language_id}", status_code=200)
async def enroll_language(language_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$addToSet": {"active_languages": language_id}},
    )
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return serialize_user(updated)


from typing import Literal
from services.subscriptions import update_subscription


class SubscriptionUpdate(BaseModel):
    subscription_status: Literal['active']
    subscription_tier: Literal['monthly', 'yearly']
    expires_at: datetime.datetime


@router.patch('/me/subscription')
async def set_subscription(body: SubscriptionUpdate, current_user=Depends(get_current_user)):
    # Students cannot grant themselves paid access. Payment handlers use the shared helper.
    if current_user.get('role') != 'admin':
        raise HTTPException(403, 'Subscription activation requires a confirmed payment')
    expiry = body.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=datetime.timezone.utc)
    if expiry <= datetime.datetime.now(datetime.timezone.utc):
        raise HTTPException(422, 'Subscription expiry must be in the future')
    db = get_db()
    await update_subscription(db, current_user['_id'], body.subscription_tier, expiry)
    return serialize_user(await db.users.find_one({'_id': current_user['_id']}))


from pydantic import Field, field_validator
import os
from services.notifications import valid_push_endpoint


class PushKeys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=200, pattern=r'^[A-Za-z0-9_=-]+$')
    auth: str = Field(min_length=1, max_length=200, pattern=r'^[A-Za-z0-9_=-]+$')


class PushSubscription(BaseModel):
    endpoint: str = Field(max_length=4096)
    keys: PushKeys

    @field_validator('endpoint')
    @classmethod
    def check_endpoint(cls, value):
        if not valid_push_endpoint(value):
            raise ValueError('Unsupported push service endpoint')
        return value


@router.get('/vapid-public-key')
async def vapid_public_key():
    key = os.getenv('VAPID_PUBLIC_KEY')
    if not key:
        raise HTTPException(503, 'Push notifications are not configured')
    return {'public_key': key}


@router.post('/me/push-subscription')
async def save_push_subscription(body: PushSubscription, current_user=Depends(get_current_user)):
    db = get_db()
    # A browser endpoint belongs to the most recently subscribing account.
    await db.users.update_many({'_id': {'$ne': current_user['_id']}, 'push_subscription.endpoint': body.endpoint},
                              {'$unset': {'push_subscription': ''}})
    await db.users.update_one({'_id': current_user['_id']}, {'$set': {'push_subscription': body.model_dump()}})
    return {'success': True}


@router.delete('/me/push-subscription')
async def remove_push_subscription(current_user=Depends(get_current_user)):
    await get_db().users.update_one({'_id': current_user['_id']}, {'$unset': {'push_subscription': ''}})
    return {'success': True}

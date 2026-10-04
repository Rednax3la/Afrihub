from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import PyMongoError

from database import get_db
from models.user import NewPassword
from services.reset_email import email_config
from services.password_reset import (
    REQUEST_MESSAGE, deliver_reset, ensure_indexes, rate_limit, reset_password, token_hash,
)

router = APIRouter(prefix='/api/auth', tags=['auth'])


class ResetRequest(BaseModel):
    email: EmailStr


class ResetConfirmation(BaseModel):
    token: str = Field(min_length=1, max_length=256)
    password: NewPassword


def client_identity(request):
    # Do not parse user-controlled X-Forwarded-For. Configure trusted proxies in
    # the ASGI server so request.client represents the verified client address.
    return request.client.host if request.client else 'unknown'


@router.post('/forgot-password', status_code=202)
async def forgot_password(body: ResetRequest, request: Request, background: BackgroundTasks):
    config = email_config()  # identical 503 for all addresses when unavailable
    db = get_db()
    try:
        await ensure_indexes(db)
        await rate_limit(db, 'request-ip', client_identity(request), 20)
        await rate_limit(db, 'request-email', str(body.email).casefold(), 5)
    except PyMongoError:
        raise HTTPException(503, 'Password recovery is temporarily unavailable. Try again later.') from None
    background.add_task(deliver_reset, db, str(body.email), config)
    return {'message': REQUEST_MESSAGE}


@router.post('/reset-password')
async def confirm_reset(body: ResetConfirmation, request: Request):
    db = get_db()
    try:
        await ensure_indexes(db)
        await rate_limit(db, 'confirm-ip', client_identity(request), 50)
        await rate_limit(db, 'confirm-token', token_hash(body.token), 20)
        await reset_password(db, body.token, body.password)
    except PyMongoError:
        raise HTTPException(503, 'Password recovery is temporarily unavailable. Try again later.') from None
    return {'message': 'Password reset successfully. Sign in with your new password.'}

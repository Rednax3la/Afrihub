import base64
import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal
from urllib.parse import quote

import httpx
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from auth import get_current_user
from database import get_db
from services.subscriptions import update_subscription

router = APIRouter(prefix='/api/payments', tags=['payments'])
PRICES = {'monthly': 1299, 'yearly': 12999}
DAYS = {'monthly': 30, 'yearly': 365}


class GooglePayment(BaseModel):
    payment_token: str = Field(min_length=1, max_length=30000)
    tier: Literal['monthly', 'yearly']


class MpesaPayment(BaseModel):
    phone: str = Field(pattern=r'^(?:\+?254|0)[17]\d{8}$')
    tier: Literal['monthly', 'yearly']


async def activate_payment(db, payment):
    if payment.get('status') == 'completed':
        return
    # Fixed expiry makes retries safe even if the process stops between these writes.
    await update_subscription(db, ObjectId(payment['user_id']), payment['tier'], payment['expires_at'])
    await db.payments.update_one({'_id': payment['_id']}, {'$set': {'status': 'completed', 'confirmed_at': datetime.now(timezone.utc)}})


async def charge_google_token(token, amount, payment_id):
    key = os.getenv('STRIPE_SECRET_KEY', '')
    if not key.startswith('sk_live_'):
        raise HTTPException(503, 'Production card payments are not configured')
    try:
        token_id = json.loads(token)['id']
        if not isinstance(token_id, str) or not token_id.startswith('tok_'):
            raise ValueError()
    except (ValueError, KeyError, TypeError):
        raise HTTPException(422, 'Invalid Google Pay gateway token')
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post('https://api.stripe.com/v1/payment_intents',
                auth=(key, ''), headers={'Idempotency-Key': payment_id}, data={
                    'amount': str(amount * 100), 'currency': 'kes', 'confirm': 'true',
                    'payment_method_types[]': 'card', 'payment_method_data[type]': 'card',
                    'payment_method_data[card][token]': token_id,
                    'error_on_requires_action': 'true',
                    'metadata[vernaculearn_payment_id]': payment_id,
                })
            if not response.is_success:
                raise HTTPException(402, 'Card payment was not confirmed. Try M-Pesa or another card.')
            data = response.json()
            if (data.get('status') != 'succeeded' or data.get('amount_received') != amount * 100
                    or data.get('currency') != 'kes' or not data.get('livemode')):
                raise HTTPException(402, 'Card payment was not confirmed')
            return data['id']
    except httpx.HTTPError:
        raise HTTPException(502, 'Payment processor unavailable. Retry the same payment.')


@router.post('/google-pay')
async def google_pay(body: GooglePayment, current_user=Depends(get_current_user)):
    mode = os.getenv('GOOGLE_PAY_ENVIRONMENT', 'PRODUCTION').upper()
    if mode not in ('TEST', 'PRODUCTION'):
        raise HTTPException(503, 'Invalid payment environment')
    if mode == 'TEST' and os.getenv('APP_ENV', 'production') != 'development':
        raise HTTPException(503, 'Test payments are disabled outside development')
    db = get_db()
    payment_id = 'google-' + hashlib.sha256(body.payment_token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    await db.payments.update_one({'_id': payment_id}, {'$setOnInsert': {
        'user_id': str(current_user['_id']), 'tier': body.tier, 'provider': 'google-pay',
        'amount': PRICES[body.tier], 'currency': 'KES', 'status': 'pending', 'environment': mode,
        'created_at': now, 'expires_at': now + timedelta(days=DAYS[body.tier]),
    }}, upsert=True)
    payment = await db.payments.find_one({'_id': payment_id})
    if payment['user_id'] != str(current_user['_id']) or payment['tier'] != body.tier or payment['environment'] != mode:
        raise HTTPException(409, 'Payment token already belongs to another purchase')
    if payment['status'] != 'completed':
        if mode == 'PRODUCTION':
            processor_id = await charge_google_token(body.payment_token, payment['amount'], payment_id)
            await db.payments.update_one({'_id': payment_id}, {'$set': {'processor_id': processor_id}})
        await activate_payment(db, payment)
    return {'success': True, 'message': 'Subscription activated'}


def mpesa_config():
    names = ['MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET', 'MPESA_SHORTCODE', 'MPESA_PASSKEY', 'MPESA_CALLBACK_URL', 'MPESA_CALLBACK_SECRET']
    config = {name: os.getenv(name, '') for name in names}
    if not all(config.values()) or not config['MPESA_CALLBACK_URL'].startswith('https://'):
        raise HTTPException(503, 'M-Pesa is not configured')
    mode = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
    if mode not in ('sandbox', 'production'):
        raise HTTPException(503, 'Invalid M-Pesa environment')
    config['base'] = 'https://api.safaricom.co.ke' if mode == 'production' else 'https://sandbox.safaricom.co.ke'
    return config


async def mpesa_request(path, data, config):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            auth = await client.get(config['base'] + '/oauth/v1/generate?grant_type=client_credentials',
                                    auth=(config['MPESA_CONSUMER_KEY'], config['MPESA_CONSUMER_SECRET']))
            auth.raise_for_status()
            token = auth.json()['access_token']
            response = await client.post(config['base'] + path, json=data, headers={'Authorization': f'Bearer {token}'})
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(502, 'M-Pesa is unavailable. Please try again.')


def mpesa_credentials(config):
    timestamp = datetime.now(timezone(timedelta(hours=3))).strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((config['MPESA_SHORTCODE'] + config['MPESA_PASSKEY'] + timestamp).encode()).decode()
    return {'BusinessShortCode': config['MPESA_SHORTCODE'], 'Password': password, 'Timestamp': timestamp}


@router.post('/mpesa/stk-push')
async def stk_push(body: MpesaPayment, current_user=Depends(get_current_user)):
    config = mpesa_config()
    phone = body.phone.lstrip('+')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    callback = config['MPESA_CALLBACK_URL']
    callback += ('&' if '?' in callback else '?') + 'secret=' + quote(config['MPESA_CALLBACK_SECRET'], safe='')
    response = await mpesa_request('/mpesa/stkpush/v1/processrequest', {
        **mpesa_credentials(config), 'TransactionType': 'CustomerPayBillOnline', 'Amount': PRICES[body.tier],
        'PartyA': phone, 'PartyB': config['MPESA_SHORTCODE'], 'PhoneNumber': phone,
        'CallBackURL': callback, 'AccountReference': 'Vernaculearn', 'TransactionDesc': body.tier + ' subscription',
    }, config)
    if str(response.get('ResponseCode')) != '0' or not response.get('CheckoutRequestID'):
        raise HTTPException(502, 'M-Pesa could not initiate this payment')
    checkout_id = response['CheckoutRequestID']
    now = datetime.now(timezone.utc)
    await get_db().payments.update_one({'_id': 'mpesa-' + checkout_id}, {'$setOnInsert': {
        'user_id': str(current_user['_id']), 'tier': body.tier, 'provider': 'mpesa', 'status': 'pending',
        'phone': phone, 'amount': PRICES[body.tier], 'currency': 'KES', 'created_at': now,
        'checkout_id': checkout_id, 'expires_at': now + timedelta(days=DAYS[body.tier]),
    }}, upsert=True)
    return {'checkout_request_id': checkout_id, 'message': 'Check your phone and enter your M-Pesa PIN.'}


async def confirm_mpesa(db, payment):
    if payment['status'] == 'completed':
        return
    config = mpesa_config()
    result = await mpesa_request('/mpesa/stkpushquery/v1/query', {
        **mpesa_credentials(config), 'CheckoutRequestID': payment['checkout_id'],
    }, config)
    code = str(result.get('ResultCode', ''))
    if code == '0':
        await activate_payment(db, payment)
    elif code in ('1032', '1037', '1', '2001'):
        await db.payments.update_one({'_id': payment['_id'], 'status': {'$ne': 'completed'}}, {'$set': {'status': 'failed'}})


@router.post('/mpesa/callback')
async def mpesa_callback(request: Request, secret: str = Query('')):
    expected = os.getenv('MPESA_CALLBACK_SECRET', '')
    if not expected or not secrets.compare_digest(secret, expected):
        raise HTTPException(403, 'Invalid callback')
    try:
        callback = (await request.json())['Body']['stkCallback']
        checkout_id = callback['CheckoutRequestID']
    except (ValueError, KeyError, TypeError):
        raise HTTPException(422, 'Invalid callback payload')
    db = get_db()
    payment = await db.payments.find_one({'_id': 'mpesa-' + checkout_id})
    if not payment:
        raise HTTPException(404, 'Unknown checkout')
    # Independently query Daraja; a callback alone can never activate a subscription.
    await confirm_mpesa(db, payment)
    return {'ResultCode': 0, 'ResultDesc': 'Accepted'}


@router.get('/mpesa/{checkout_id}')
async def mpesa_status(checkout_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    query = {'_id': 'mpesa-' + checkout_id, 'user_id': str(current_user['_id'])}
    payment = await db.payments.find_one(query)
    if not payment:
        raise HTTPException(404, 'Payment not found')
    if payment['status'] == 'pending':
        await confirm_mpesa(db, payment)
        payment = await db.payments.find_one(query)
    return {'status': payment['status']}

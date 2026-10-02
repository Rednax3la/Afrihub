"""Generate private local VAPID settings without printing or committing secrets."""
from pathlib import Path
from py_vapid import Vapid
from py_vapid.utils import b64urlencode
from cryptography.hazmat.primitives import serialization

output = Path(__file__).resolve().parents[1] / '.env.push.local'
if output.exists():
    raise SystemExit('Keys already exist in backend/.env.push.local; preserving them.')
v = Vapid()
v.generate_keys()
private = v.private_key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
public = v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
output.write_text('VAPID_PRIVATE_KEY=' + b64urlencode(private) + '\nVAPID_PUBLIC_KEY=' + b64urlencode(public) + '\nVAPID_CLAIM_EMAIL=hello@vernaculearn.africa\n', encoding='utf-8')
print('Generated keys in backend/.env.push.local. Copy these settings into backend/.env or your deployment secrets.')

"""Policy for NEW bcrypt passwords only; legacy login stays compatible."""
import re
import string

PASSWORD_POLICY = (
    'Use at least 9 characters, an uppercase letter (A-Z), a lowercase letter (a-z), '
    'a digit (0-9), and an ASCII punctuation character (for example !, @, or _). '
    'Passwords must fit within 72 UTF-8 bytes and cannot contain null characters.'
)


def validate_new_password(value: str) -> str:
    if (len(value) < 9 or len(value.encode('utf-8')) > 72 or '\x00' in value
            or not re.search(r'[A-Z]', value) or not re.search(r'[a-z]', value)
            or not re.search(r'[0-9]', value) or not any(c in string.punctuation for c in value)):
        raise ValueError(PASSWORD_POLICY)
    return value

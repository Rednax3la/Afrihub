import os

# The suite must not depend on live DNS. Syntax, typo and disposable-domain
# checks still run; only the MX lookup is skipped.
os.environ.setdefault("EMAIL_DELIVERABILITY_CHECK", "false")

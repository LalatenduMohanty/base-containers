"""ODH Base Container Image Tests."""

import re

# Common paths used across tests
APP_ROOT = "/opt/app-root"
WORKDIR = f"{APP_ROOT}/src"

# Matches the credential portion of URLs like https://token@host or
# https://user:pass@host.  The ``/`` exclusion in the character class
# prevents greedy over-redaction of URLs where ``@`` appears after a
# path component (e.g. OCI references like
# ``https://registry.example.com/image@sha256:...``).
_URL_CREDENTIAL_RE = re.compile(r"(https?://)([^@\s/]+)@")


def redact_url_credentials(text: str) -> str:
    """Replace embedded credentials in URLs with ``****``.

    pip only redacts ``user:password@host`` URLs; bare ``token@host``
    credentials pass through unmasked.  This helper catches both forms
    so that stderr can be safely included in assertion messages without
    leaking secrets to CI logs.
    """
    return _URL_CREDENTIAL_RE.sub(r"\1****@", text)

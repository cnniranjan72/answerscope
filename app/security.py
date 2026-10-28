"""Bearer-token authentication against server-configured identities.

The caller presents a token; the server maps it to (name, role) from its own
configuration. No request field can assert a role or actor name.
"""
from __future__ import annotations

import hmac

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Identity
from app.errors import Forbidden, Unauthenticated

_bearer = HTTPBearer(auto_error=False, description="ANALYST_TOKEN or REVIEWER_TOKEN from server .env")


def current_identity(request: Request,
                     creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> Identity:
    if creds is None or creds.scheme.lower() != "bearer":
        raise Unauthenticated("missing bearer token")
    for token, identity in request.app.state.settings.tokens.items():
        if hmac.compare_digest(token.encode(), creds.credentials.encode()):
            return identity
    raise Unauthenticated("invalid token")


def require(*roles: str):
    def dep(identity: Identity = Depends(current_identity)) -> Identity:
        if identity.role not in roles:
            raise Forbidden(f"role '{identity.role}' may not perform this action",
                            {"required_roles": list(roles)})
        return identity
    return dep

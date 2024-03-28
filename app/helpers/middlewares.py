from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param

from app.helpers.exceptions import AuthenticationFailedError
from app.helpers.cryptography import jwt_decode


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise AuthenticationFailedError
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise AuthenticationFailedError(message="Invalid authentication credentials")
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


security_bearer = CustomHTTPBearer()


async def get_user_organization(
        credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
):
    organization_id = jwt_decode(credentials.credentials).get("organizationId")
    if not organization_id:
        raise AuthenticationFailedError
    return organization_id

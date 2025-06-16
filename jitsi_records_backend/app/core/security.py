import aiohttp
from fastapi import Depends, Header, HTTPException

from app.core.config import get_settings, BaseSettings
from app.core.http_client import http_client


async def verify_bearer_token(authorization: str = Header(...), settings: BaseSettings = Depends(get_settings)) -> None:
    if authorization != f"Bearer {settings.RECORDS_HANDLER_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid authorization token")


async def check_greyt_auth_token(http_session: aiohttp.ClientSession = Depends(http_client),
                                 access_token: str = Header(...),
                                 uid: str = Header(...),
                                 client: str = Header(...),
                                 settings: BaseSettings = Depends(get_settings)):
    url = f'{settings.GREYT_HOST}/api/v1/auth/validate_token/'
    r = await http_session.get(url, headers={'access-token': access_token, 'client': client, 'uid': uid})
    try:
        json = await r.json()
        if not json['success']:
            errors = json['errors'][0] if len(json['errors']) == 1 else ''
            raise HTTPException(status_code=401, detail=errors)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Authentication failed.")
    return json['data']

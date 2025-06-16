import uvicorn

from app.core.config import settings

if __name__ == '__main__':
    params = settings.get_uvicorn_init_keys()
    uvicorn.run("app.main:app", **params)

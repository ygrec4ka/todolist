import uvicorn
from fastapi import FastAPI

from core.routers.users import router as users_router
from core.routers.auth import router as auth_router


app = FastAPI()


app.include_router(users_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
    )

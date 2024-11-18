from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from api.endpoints import (user_rouetr, add_material_router,material_name_router,site_address_router,vendor_router)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_rouetr, prefix="/api", tags=["user Routes"])
app.include_router(add_material_router, prefix="/api", tags=["Add Material data Routes"])

app.include_router(material_name_router, prefix="/api", tags=["new add Material name Routes"])
app.include_router(site_address_router, prefix="/api", tags=["Add new  site address data Routes"])
app.include_router(vendor_router, prefix="/api", tags=["Add new vendor data Routes"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload= True, host="0.0.0.0")
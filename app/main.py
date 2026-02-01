from dotenv import load_dotenv
load_dotenv()

import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import platform #pour récup la version de Python

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database.db import init_db 
import app.api.auth as auth_router
import app.api.users as users_router
import app.api.product as product_router
import app.api.order as order_router
import app.api.admin as admin_router
import app.api.frontend as frontend_router
import app.api.contact as contact_router
from app.core.limiter import limiter


init_db()
app = FastAPI(title="Vulnerable API demo")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


#vulnérabilité CORS trop permissif API8
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #* au lieu du domaine du front-end
    allow_credentials=True,
    allow_methods=["*"],  #autorise tous les verbes (GET, POST, DELETE etc)
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(users_router.router, tags=["Users"])
app.include_router(product_router.router, tags=["Products"])
app.include_router(admin_router.router, tags=["Admin"])
app.include_router(order_router.router, tags=["Orders"])
app.include_router(contact_router.router)
app.include_router(frontend_router.router)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "vulnerable-api",
        "version": "1.0.0-beta",      #indique que c'est une version instable
        "environment": "production-v1",  #vrai système
        "framework": f"FastAPI {fastapi.__version__}",
        "system": platform.system(),  # Linux/Windows ?
        "language": f"Python {platform.python_version()}", #donne la version Python
        "database_status": "connected (SQLite 3.39.2)", #donne le type de BDD
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vulnerable API Demo. Check /docs for endpoints!"}
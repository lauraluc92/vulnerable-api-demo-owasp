import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app_secure.core.limiter import limiter
from app_secure.database.db import init_db
import app_secure.api.auth as auth_router
import app_secure.api.users as users_router
import app_secure.api.product as product_router
import app_secure.api.order as order_router
import app_secure.api.admin as admin_router
import app_secure.api.frontend as frontend_router
import app_secure.api.contact as contact_router
app = FastAPI(title="Secure Shop API", description="Port 8001", version="1.0-SECURE", docs_url=None,       # Désactive /docs
    redoc_url=None, 
    openapi_url=None )

#protection api4
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="app_secure/static"), name="static")
app.add_middleware(SlowAPIMiddleware)

#protection api8
origins = [] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

#protection api8 : security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "frame-ancestors 'none';"
    )
    
    # CSP : bloque les scripts tiers (Anti-XSS)
    response.headers["Content-Security-Policy"] = csp_policy
    # anti-MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Anti-Clickjacking (Interdit l'affichage en iframe)
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "secure-shop-api"}

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(users_router.router, tags=["Users"])
app.include_router(product_router.router, tags=["Products"])
app.include_router(order_router.router, tags=["Orders"])
app.include_router(contact_router.router)
app.include_router(frontend_router.router)
#défense contre la reconnaissance API9: on change le nom des routes Admin
SECRET_ADMIN_URL = os.getenv("SECRET_ADMIN_URL")

app.include_router(
    admin_router.router, 
    prefix=SECRET_ADMIN_URL, 
    tags=["Admin"],
    include_in_schema=False #de plus, les routes ne sont pas visibles dans doc Swagger
)
@app.on_event("startup")
def on_startup():
    init_db()
    print("SERVEUR SECURISE DEMARRE SUR LE PORT 8001")
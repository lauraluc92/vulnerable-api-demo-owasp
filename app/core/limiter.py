from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

#pour api6
def get_ip_address(request: Request):
    #si le header "X-Forwarded-For" est présent (envoyé par le script d'attaque), on l'utilise (pour simuler des gens
    #avec plusieurs ips)
    #sinon, on prend l'IP réelle (127.0.0.1).
    #dans la vraie vie on fait pas confiance à ce header
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded
    return get_remote_address(request)

limiter = Limiter(key_func=get_ip_address)
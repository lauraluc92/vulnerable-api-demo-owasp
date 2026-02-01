from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

# MÊME LOGIQUE QUE LA VERSION VULNÉRABLE
# On conserve cette fonction pour simuler un environnement réaliste
# où un attaquant dispose d'un Botnet (plusieurs IPs réelles).
# La défense contre cela ne se fera pas ici (au niveau de l'IP),
# mais au niveau des endpoints (Global Limit ou Captcha).

def get_ip_address(request: Request):
    # Si le header "X-Forwarded-For" est présent (simulation de proxy/botnet),
    # on l'utilise comme identifiant unique.
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded
    return get_remote_address(request)

limiter = Limiter(key_func=get_ip_address)
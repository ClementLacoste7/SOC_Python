# SOC Python

API de suivi d'incidents de sécurité fictifs (projet Ynov B2 Cybersécurité, groupe 1).
FastAPI, SQLModel, SQLite, JWT, pytest.

Un déclarant crée des incidents et consulte les siens.
Un analyste consulte tous les incidents, les prend en charge et les clôture.

## Installation

Python 3.12 ou plus récent. Commandes pour Windows PowerShell, à la racine du dépôt.

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

```
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Coller la valeur affichée après `SECRET_KEY=` dans `.env`.
Le fichier `.env` n'est pas suivi par Git. L'API refuse de démarrer sans `SECRET_KEY`.

| Variable | Rôle | Valeur par défaut |
|---|---|---|
| SECRET_KEY | clé de signature des JWT | aucune, obligatoire |
| ACCESS_TOKEN_EXPIRE_MINUTES | durée de vie d'un jeton | 30 |
| DATABASE_URL | base SQLite | sqlite:///./incidents.db |
| LOG_LEVEL | niveau des journaux | INFO |

## Données de démonstration

```
python cli.py reset-demo
```

La commande vide la base et recrée trois comptes et trois incidents fictifs.
Elle refuse de s'exécuter si la base contient un compte qui n'est pas un compte de démonstration.

| Compte | Rôle | Mot de passe |
|---|---|---|
| alice | declarant | Demo1234! |
| bob | declarant | Demo1234! |
| carol | analyste | Demo1234! |

## Lancer l'API

```
uvicorn app.main:app --reload
```

Swagger UI : http://127.0.0.1:8000/docs
Cliquer sur Authorize et saisir un compte de démonstration.

## Routes

| Méthode | Chemin | Rôle | Action |
|---|---|---|---|
| POST | /token | tous | se connecter et obtenir un JWT |
| POST | /incidents | connecté | créer un incident |
| GET | /incidents | connecté | lister les incidents visibles, filtres `etat` et `gravite` |
| GET | /incidents/{id} | auteur ou analyste | lire un incident |
| PATCH | /incidents/{id}/start | analyste | passer de nouveau à en_cours |
| PATCH | /incidents/{id}/close | analyste | passer de en_cours à clos, conclusion obligatoire |

Valeurs acceptées :
- etat : nouveau, en_cours, clos
- gravite (champ `severity`) : faible, moyenne, forte
- catégorie (champ `category`) : courriel_suspect, poste_perdu, compte_compromis, autre

Codes de refus : 401 connexion absente ou invalide, 403 action interdite, 404 identifiant inconnu,
409 état incompatible, 422 entrée invalide.

## CLI

```
python cli.py bilan --format json
python cli.py reset-demo
```

`bilan` affiche sur stdout le nombre d'incidents par état et par gravité.
La CLI lit la même base que l'API et n'a pas besoin du serveur HTTP.

## Tests et qualité

```
pytest
ruff check .
```

Les tests utilisent une base dédiée `test_incidents.db`, recréée avant chaque test.
Ils ne touchent pas à la base de démonstration et fonctionnent sans fichier `.env`.

## Scénario de démonstration

1. `python cli.py reset-demo` puis `uvicorn app.main:app --reload`
2. Avec alice : POST /incidents, noter l'identifiant renvoyé (4 après une remise à zéro)
3. Avec bob : GET /incidents/4, réponse 403
4. Avec carol : PATCH /incidents/4/close, réponse 409 car l'incident est encore nouveau
5. Avec carol : PATCH /incidents/4/start puis PATCH /incidents/4/close avec une conclusion, réponses 200
6. Avec carol : GET /incidents?etat=clos&gravite=forte
7. `python cli.py bilan --format json` puis `pytest`

Exemple de corps pour POST /incidents :

```
{"title": "Courriel suspect", "category": "courriel_suspect", "severity": "forte"}
```

## Organisation du code

```
app/config.py               configuration lue depuis .env
app/database.py             moteur SQLite et session
app/models.py               tables User et Incident
app/schemas.py              enums et modèles d'entrée et de sortie
app/errors.py               erreurs métier
app/security.py             hachage bcrypt et JWT
app/deps.py                 utilisateur courant à partir du jeton
app/user_repository.py      accès base des utilisateurs
app/incident_repository.py  accès base des incidents
app/auth_service.py         connexion
app/incident_service.py     règles des incidents et bilan
app/seed.py                 données de démonstration
app/routes/                 routes HTTP
app/main.py                 application FastAPI
cli.py                      commandes bilan et reset-demo
tests/                      tests pytest
```

## Vérification depuis une copie propre

Étapes rejouées le 30/09/2026 sous Windows 11 avec Python 3.13, à partir d'un clone neuf du dépôt
et d'un environnement virtuel neuf : installation, configuration, `reset-demo`, `bilan`, lancement
de l'API et scénario de démonstration.
Résultat : toutes les étapes fonctionnent, `ruff check .` ne signale aucune erreur et les 28 tests passent.

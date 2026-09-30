# Note de projet

Groupe 1, suivi des incidents de sécurité. Binôme : Clément Lacoste et Ilyas Kehili.

## Répartition du travail

Clément a pris en charge le socle et l'authentification : structure du dépôt, configuration,
base de données, table des utilisateurs, hachage des mots de passe, JWT, route /token,
utilisateur courant, application FastAPI, données de démonstration, commande reset-demo,
tests d'authentification et README.

Ilyas a pris en charge les incidents : enums et schémas d'entrée et de sortie, erreurs métier,
table des incidents, accès à la base, règles (propriété, prise en charge, clôture), routes
/incidents, commande bilan, tests du service, de l'API et de la CLI, journaux.

Chacun a travaillé sur sa branche avec son propre compte, puis les branches ont été fusionnées
sur main quand les tests passaient. L'usage de l'IA est décrit dans USAGE_IA.md.

## Schéma du programme

```
Client HTTP  ->  routes + deps  ->  services  ->  repositories  ->  SQLite
CLI locale   ------------------->  services  ->  repositories  ->  SQLite
```

- routes et deps : HTTP et vérification du jeton
- services : règles (rôle, propriété, états)
- repositories : seul accès à la base

Exemple avec PATCH /incidents/4/close : validation du corps (422), vérification du jeton (401),
puis le service contrôle le rôle (403), l'existence (404) et l'état (409) avant d'enregistrer.

## Décision 1 : 403 pour l'incident d'un autre déclarant

Un 404 aurait caché l'existence de l'incident. Nous avons gardé 403, car le sujet l'associe aux
actions interdites. Un déclarant peut donc deviner qu'un numéro existe, sans jamais lire son contenu.

## Décision 2 : erreurs métier séparées de HTTP

Les services lèvent nos propres erreurs, et un seul gestionnaire dans main.py les traduit en
réponse HTTP. La CLI et les tests utilisent ainsi les mêmes règles sans serveur.

## Limites connues

- Pas d'inscription, de renouvellement ni de révocation des jetons.
- Pas de limite sur les tentatives de connexion.
- Liste des incidents non paginée.
- SQLite local sans outil de migration.
- Comptes créés uniquement par reset-demo, en HTTP local sans HTTPS.

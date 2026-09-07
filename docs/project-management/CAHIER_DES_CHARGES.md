# Cahier des charges — Pac-Man (projet 42, groupe de 2)

Basé sur le sujet officiel v1.5. Découpage en deux lots de taille et de
complexité équivalentes, pensés pour être développés en parallèle avec le
moins de dépendances croisées possible. Les interfaces entre les deux lots
sont figées dès le départ (voir "Contrats d'interface") pour éviter les
blocages.

---

## Lot A — Moteur, données & progression
*(config, maze loader, joueur, collectibles, score, progression, highscore)*

1. **Configuration (spec 5.1–5.3)**
   - Parsing du fichier JSON avec support des commentaires (`#`, éventuellement `//` `/* */`)
   - Validation, valeurs par défaut robustes, gestion propre des clés
     manquantes/invalides/inconnues — **jamais de traceback**
   - Doc des clés dans le README (section Configuration)

2. **Intégration du package A-Maze-ing (spec 5.4, 6.1)**
   - Loader qui s'adapte à l'interface du package reçu (pas l'inverse)
   - Niveau 1 : seed fixe (42) ; niveaux suivants : génération aléatoire
   - `PERFECT=False`, gestion propre des échecs de génération

3. **Joueur (spec 6.2)**
   - Déplacement 4 directions (flèches / WASD), collisions avec les murs
   - Vies, respawn au centre, perte de vie, game over

4. **Pacgums / Super-pacgums (spec 6.4)**
   - Placement (corridors / 4 coins), état "mangé", décompte de fin de niveau

5. **Scoring (spec 6.6)**
   - +X pacgum, +Y super-pacgum, +Z fantôme mangé (valeurs venant de la config)

6. **Progression de partie (spec 6.7)**
   - ≥ 10 niveaux, timer par niveau, passage de niveau, conservation
     score/vies entre niveaux, pause/reprise, fin de partie (victoire/défaite)

7. **Highscore system (spec 5.5)**
   - Persistance JSON, robustesse aux fichiers absents/corrompus
   - Validation nom (≤10 car., alphanumérique + espaces) et score (entier ≥ 0)
   - Top 10, chargement au démarrage / sauvegarde en fin de partie

**Livrables du lot A :** `src/pacman/config/`, `src/pacman/highscore/`,
la logique de `src/pacman/game/` liée au joueur/score/progression, tests
unitaires associés (config parsing, highscore, scoring).

---

## Lot B — Rendu, IA fantômes, UI & packaging
*(graphique, fantômes, menus/HUD, cheat mode, déploiement)*

1. **Choix et setup de la lib graphique (spec chap. 4)**
   - Choix justifié (MLX ou équivalent strict — voir contrainte du sujet)
   - Boucle de rendu, gestion des inputs clavier

2. **Fantômes (spec 6.3)**
   - 4 fantômes, un par coin, déplacement autonome dans les corridors
   - Comportement de poursuite (à définir : distance, aléatoire...) quand
     non-mangeables
   - Comportement de fuite quand mangeables (après super-pacgum), respawn
     différé après avoir été mangés

3. **Interface utilisateur (spec 6.8)**
   - Main menu (Start / Highscores / Instructions / Exit)
   - HUD en jeu (score, vies, niveau, temps restant)
   - Menu pause (resume / retour menu)
   - Écrans Game Over et Victoire (score final + saisie du nom)

4. **Cheat mode (spec 6.5)**
   - Invincibilité, skip de niveau, freeze fantômes, vies bonus, vitesse++
   - Doit réellement faciliter la review (accès simple, ex. touches dédiées)

5. **Packaging & déploiement (spec chap. 7)**
   - Build fonctionnel packagé et publié en privé/non répertorié sur
     Steam ou Itch.io
   - Script/spec de packaging à la racine du repo
   - Instructions minimales embarquées dans le package

**Livrables du lot B :** `src/pacman/ui/`, la logique fantômes dans
`src/pacman/game/`, `packaging/`, tests unitaires associés (IA fantômes,
transitions d'écrans si testables).

---

## Contrats d'interface (à valider ensemble avant de coder)

Pour travailler en parallèle sans se bloquer, définissez ensemble dès le
lancement (et figez dans un fichier `game/types.py` ou équivalent) :

- La structure de données `GameConfig` retournée par le loader (Lot A)
  et consommée par le rendu/UI (Lot B).
- La représentation du labyrinthe une fois adapté depuis A-Maze-ing
  (grille, coordonnées, murs/corridors) — Lot A produit, Lot B affiche.
- L'état de jeu partagé (position joueur, fantômes, score, vies, temps
  restant, liste des pacgums restants) — objet ou dataclass commun.
- Les événements/callbacks du cheat mode (Lot B) qui doivent pouvoir
  modifier l'état de progression (Lot A) : invincibilité, skip niveau, etc.

## Travail commun (à vous deux, pas divisible proprement)

- Architecture initiale (squelette de classes, découpage modules) — 1
  session ensemble avant de vous séparer sur les lots.
- README.md (chaque lot documente sa partie, mais la structure/relecture
  est commune).
- Tests d'intégration bout-en-bout (`make run` fonctionnel de A à Z).
- Documents de gestion de projet dans ce dossier (planning, suivi,
  analyse de risques, tests d'acceptation, organisation d'équipe).
- Revue de code croisée avant chaque merge sur la branche principale.

## Suivi

| Élément | Emplacement suggéré |
|---|---|
| Planning / Kanban | `docs/project-management/planning.md` ou lien Trello/GitHub Projects |
| Suivi d'avancement vs planning | `docs/project-management/progress.md` |
| Analyse de risques | `docs/project-management/risks.md` |
| Organisation d'équipe | `docs/project-management/team-organization.md` |
| Plan de tests d'acceptation | `docs/project-management/acceptance-tests.md` |

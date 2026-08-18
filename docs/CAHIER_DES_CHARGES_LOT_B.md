# Cahier des charges — Lot B (Rendu, IA fantômes, UI & Packaging)

Ta partie du projet Pac-Man (binôme). Basé sur le sujet officiel v1.5.
Ton mate gère la config, le maze loader, le joueur, les collectibles, le
score et le highscore (Lot A) — tu n'as pas à y toucher, mais tu en
dépends via les contrats d'interface ci-dessous.

---

## 1. Choix de la librairie graphique (spec chap. 4)

⚠️ Contrainte stricte du sujet :
> Une lib est "similaire à MLX" seulement si **chaque fonction que tu
> utilises** a un équivalent dans MLX. Si une fonction que tu utilises
> n'a pas d'équivalent MLX, elle n'est pas autorisée.

- [x] Lib choisie : **pygame**, en usage restreint au sous-ensemble ayant
  un équivalent MLX. `requirements.txt` mis à jour.
  - Autorisé : `display.set_mode`, `display.flip`/`update`,
    `draw.rect`/`circle`, `surface.fill`/`blit`, `image.load`,
    `event.get` + `KEYDOWN`/`K_*`, `time.Clock().tick`,
    `font.Font` + `.render` (texte).
  - Interdit (pas d'équivalent MLX) : `pygame.mixer` (son),
    `pygame.sprite` collision helpers (`spritecollide`...), joystick,
    réseau. Faire les collisions "à la main" (comparaison de coordonnées).
- [ ] Documenter la liste exacte des fonctions pygame utilisées dans le
  README (section Implementation), avec leur équivalent MLX en face.
- [ ] Mettre en place la boucle de rendu de base (fenêtre, clear, flip)
  et la capture des inputs clavier (flèches + WASD).

## 2. Fantômes (spec 6.3)

- [ ] 4 fantômes, un par coin du labyrinthe au début du niveau.
- [ ] Déplacement autonome dans les corridors uniquement (pas de
  traversée de mur).
- [ ] Comportement de poursuite quand non-mangeables — comportement libre
  à définir et documenter (distance au joueur, semi-aléatoire, un
  comportement différent par fantôme façon Blinky/Pinky/Inky/Clyde...).
- [ ] Comportement de fuite quand mangeables (après super-pacgum).
- [ ] État "mangé" → disparition puis respawn dans son coin après un
  délai (5-10s).
- [ ] Gérer proprement la collision avec le joueur dans les deux sens
  (fantôme mangeable → +Z points ; fantôme normal → joueur perd une vie),
  en coordination avec le Lot A pour l'appel aux fonctions de score/vie.

## 3. Interface utilisateur (spec 6.8)

- [ ] **Main Menu** : Start Game / View Highscores (top 10, lues via le
  module highscore du Lot A) / Instructions / Exit.
- [ ] **HUD en jeu** (toujours visible) : score courant, vies restantes,
  niveau courant, temps restant.
- [ ] **Menu pause** : Resume / Retour au menu principal.
- [ ] **Écran Game Over** : score final + saisie du nom (→ transmis au
  module highscore du Lot A).
- [ ] **Écran Victoire** : score final + message de félicitations + saisie
  du nom.
- [ ] Enchaînement complet du Game Loop : Main Menu → Start → Win/Lose →
  Saisie nom → Retour Main Menu.

## 4. Cheat mode (spec 6.5)

Doit *réellement* faciliter la review par les pairs — accès simple
(ex. touches dédiées affichées à l'écran ou dans les instructions).

- [ ] Invincibilité (aucune vie perdue, fantômes ne touchent pas le joueur)
- [ ] Level skip (victoire immédiate du niveau en cours)
- [ ] Ghost freeze (les fantômes arrêtent de bouger)
- [ ] Vies bonus (ajout de vies)
- [ ] Vitesse augmentée du joueur
- [ ] Optionnel : toute autre feature utile (ex. voir tous les fantômes
  en mode debug, sauter directement à un niveau donné...)

## 5. Packaging & déploiement (spec chap. 7)

- [ ] Build fonctionnel packagé et publié en **privé/non répertorié** sur
  Steam ou Itch.io (gratuit).
- [ ] Script ou spec de packaging à la racine du repo (dossier
  `packaging/`).
- [ ] Instructions minimales embarquées dans le package livré (contrôles,
  options, configuration).
- [ ] Être prêt à régénérer le package pendant la peer-review.

---

## Contrats d'interface avec le Lot A (à valider ensemble avant de coder)

Tu consommes ces éléments produits par ton mate — mettez-vous d'accord
sur leur forme exacte dès le départ, idéalement dans un fichier partagé
type `game/types.py` :

- **`GameConfig`** : objet/dataclass retourné par le loader de config
  (lives, points_per_*, level_max_time, etc.) — tu l'utilises pour le HUD
  et les règles d'affichage.
- **Représentation du labyrinthe** : grille adaptée depuis A-Maze-ing
  (murs/corridors, coordonnées) — tu dois savoir comment la lire pour
  dessiner et faire naviguer les fantômes dedans.
- **État de jeu partagé** : position joueur, score, vies, temps restant,
  pacgums restants — objet commun que tu lis pour le HUD et que tes
  écrans/cheat mode peuvent modifier (ex. skip niveau, vies bonus).
- **API du module highscore** (ex. `load_highscores()`,
  `save_highscore(name, score)`) — utilisée par ton Main Menu et tes
  écrans de fin de partie.
- **Callbacks du cheat mode → état de progression** : tu déclenches les
  actions (invincibilité, skip, freeze...) mais elles modifient l'état
  géré côté Lot A — définir la signature de ces fonctions ensemble.

## Livrables

- `src/pacman/ui/` (menus, HUD, écrans, gestion des inputs)
- Logique des fantômes dans `src/pacman/game/` (fichier dédié, ex.
  `ghost.py`, `ghost_ai.py`)
- `packaging/` (script/spec de build + instructions)
- Tests unitaires sur ce qui est testable sans fenêtre graphique (logique
  de poursuite/fuite des fantômes, transitions d'état des menus)
- Ta partie du README : sections **Implementation** (choix de lib
  graphique + IA fantômes) et une partie de **General Software
  Architecture** côté UI/rendu

## Points d'attention

- Ne modifie pas le package A-Maze-ing assigné — adapte-toi à son
  interface, pas l'inverse (c'est dans le rôle du Lot A mais ça impacte
  directement comment tu lis le labyrinthe pour le rendu).
- Gestion d'erreurs : ton code aussi doit être robuste (pas de crash), y
  compris en cas d'échec d'init graphique ou d'input invalide.
- Le cheat mode sera testé par les reviewers : vérifie qu'il est simple
  d'accès et clairement documenté dans le README/instructions du package.

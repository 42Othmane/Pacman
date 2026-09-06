"""Gestion du score d'une partie.

Les valeurs en points viennent de la configuration. Le score ne
peut jamais décroître (spec 6.6).
"""


class Score:
    """Compteur de points d'une partie."""

    def __init__(self, pacgum: int, superpacgum: int, ghost: int) -> None:
        """Initialise le score à zéro.

        Args:
            pacgum: points gagnés en mangeant un pacgum.
            superpacgum: points gagnés en mangeant un super-pacgum.
            ghost: points gagnés en mangeant un fantôme comestible.
        """
        self.points_per_pacgum = pacgum
        self.points_per_superpacgum = superpacgum
        self.points_per_ghost = ghost
        self.value: int = 0

    def _add(self, points: int) -> None:
        """Ajoute des points au score.

        Les valeurs négatives sont ignorées : le score ne décroît jamais.
        """
        self.value += max(0, points)

    def add_pacgum(self) -> None:
        """Crédite les points d'un pacgum."""
        self._add(self.points_per_pacgum)

    def add_superpacgum(self) -> None:
        """Crédite les points d'un super-pacgum."""
        self._add(self.points_per_superpacgum)

    def add_ghost(self) -> None:
        """Crédite les points d'un fantôme mangé."""
        self._add(self.points_per_ghost)

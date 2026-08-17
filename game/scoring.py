class Score:
    def __init__(self, pacgum: int, superpacgum: int, ghost: int):

        self.pacgum = pacgum
        self.superpacgum = superpacgum
        self.ghost = ghost
        self.value: int = 0


    def add_pacgum(self) -> None:
        self.value += self.pacgum

    def add_superpacgum(self) -> None:
        self.value += self.superpacgum

    def add_ghost(self) -> None:
        self.value += self.ghost
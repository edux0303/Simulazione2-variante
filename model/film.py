from dataclasses import dataclass

@dataclass
class Film:
    id: str
    title: str
    year: int
    durata: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Film) and self.id == other.id

    def __str__(self):
        return f"{self.title} ({self.year})"
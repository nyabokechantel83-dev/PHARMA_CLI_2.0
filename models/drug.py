from dataclasses import dataclass, asdict

from utils import storage

FILE_NAME = "drugs.json"


@dataclass
class Drug:
    id: int
    name: str
    price: float
    stock: int
    category: str
    requires_rx: bool

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(row):
        return Drug(**row)


def load_drugs():
    rows = storage.read_json(FILE_NAME)
    return [Drug.from_dict(row) for row in rows]


def save_drugs(drugs):
    rows = [drug.to_dict() for drug in drugs]
    storage.write_json(FILE_NAME, rows)


def find_by_id(drug_id):
    for drug in load_drugs():
        if drug.id == drug_id:
            return drug

    return None
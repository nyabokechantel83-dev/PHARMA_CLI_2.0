import json
from pathlib import Path

from models.drug import Drug


class Pharmacist:
    def __init__(self, name, data_file="data/drugs.json"):
        self.name = name
        self.data_file = Path(data_file)

    def load_drugs(self):
        if not self.data_file.exists():
            return []

        with open(self.data_file, "r") as file:
            return json.load(file)

    def save_drugs(self, drugs):
        with open(self.data_file, "w") as file:
            json.dump(drugs, file, indent=4)

    def add_drug(self, name, price, stock, requires_prescription, category=None):
        if price <= 0:
            raise ValueError("Price must be greater than 0")

        if stock <= 0:
            raise ValueError("Stock must be greater than 0")

        drugs = self.load_drugs()

        drug = {
            "id": str(len(drugs) + 1),
            "name": name,
            "price": price,
            "stock": stock,
            "requires_prescription": requires_prescription,
            "category": category
        }

        drugs.append(drug)
        self.save_drugs(drugs)

        return drug

    def list_drugs(self):
        return self.load_drugs()

    def get_drug(self, drug_id):
        drugs = self.load_drugs()

        for drug in drugs:
            if drug["id"] == str(drug_id):
                return drug

        raise ValueError("Drug not found")

    def update_stock(self, drug_id, new_stock):
        if new_stock <= 0:
            raise ValueError("Stock must be greater than 0")

        drugs = self.load_drugs()

        for drug in drugs:
            if drug["id"] == str(drug_id):
                drug["stock"] = new_stock
                self.save_drugs(drugs)
                return drug

        raise ValueError("Drug not found")
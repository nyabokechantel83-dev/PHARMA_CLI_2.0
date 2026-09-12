class Drug:
    def __init__(self, name, price, stock, requires_prescription, category=None):
        self.id = None
        self.name = name
        self.price = price
        self.stock = stock
        self.requires_prescription = requires_prescription
        self.category = category


class DrugStore:
    def __init__(self):
        self.drugs = []

    def add_drug(self, name, price, stock, requires_prescription, category=None):
        if price <= 0:
            raise ValueError("Price must be greater than 0")

        if stock <= 0:
            raise ValueError("Stock must be greater than 0")

        drug = Drug(
            name,
            price,
            stock,
            requires_prescription,
            category
        )

        drug.id = str(len(self.drugs) + 1)
        self.drugs.append(drug)
        return drug

    def list_drugs(self):
        return self.drugs

    def get_drug(self, drug_id):
        for drug in self.drugs:
            if drug.id == str(drug_id):
                return drug

        raise ValueError("Drug not found")


_store = DrugStore()


def add_drug(name, price, stock, requires_prescription, category=None):
    return _store.add_drug(
        name,
        price,
        stock,
        requires_prescription,
        category
    )


def list_drugs():
    return _store.list_drugs()


def get_drug(drug_id):
    return _store.get_drug(drug_id)
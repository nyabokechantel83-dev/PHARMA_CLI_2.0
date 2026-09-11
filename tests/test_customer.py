from types import SimpleNamespace

from cli.customer import _list_drugs, _show_drug, _place_order


class TestListDrugs:

    def test_prints_a_message_when_the_catalog_is_empty(self, capsys, services):
        _list_drugs(args=None, services=services)

        output = capsys.readouterr().out
        assert "No drugs in the catalog yet." in output

    def test_prints_every_drug_that_was_added(self, capsys, services, drug_service):
        drug_service.add_drug(name="Panadol", price=50, stock=20, requires_prescription=False)
        drug_service.add_drug(name="Amoxicillin", price=150, stock=10, requires_prescription=True)

        _list_drugs(args=None, services=services)

        output = capsys.readouterr().out
        assert "Panadol" in output
        assert "Amoxicillin" in output


class TestShowDrug:

    def test_shows_details_for_a_valid_drug(self, capsys, services, drug_service):
        drug = drug_service.add_drug(name="Panadol", price=50, stock=20, requires_prescription=False)
        args = SimpleNamespace(drug_id=drug.id)

        _show_drug(args=args, services=services)

        output = capsys.readouterr().out
        assert "Panadol" in output
        assert "50" in output

    def test_shows_a_clean_error_for_an_unknown_drug(self, capsys, services):
        args = SimpleNamespace(drug_id="does-not-exist")

        _show_drug(args=args, services=services)

        output = capsys.readouterr().out
        assert "Error" in output


class TestPlaceOrder:

    def test_confirms_instantly_for_a_non_prescription_drug(self, capsys, services, drug_service):
        drug = drug_service.add_drug(
            name="Panadol", price=50, stock=20, requires_prescription=False, category="analgesic"
        )
        args = SimpleNamespace(drug_id=drug.id, prescription_ref=None)

        _place_order(args=args, services=services)

        output = capsys.readouterr().out
        assert "CONFIRMED" in output

    def test_creates_a_pending_claim_for_a_prescription_drug(self, capsys, services, drug_service):
        drug = drug_service.add_drug(name="Amoxicillin", price=150, stock=10, requires_prescription=True)
        args = SimpleNamespace(drug_id=drug.id, prescription_ref="RX-1001")

        _place_order(args=args, services=services)

        output = capsys.readouterr().out
        assert "PENDING" in output

    def test_shows_an_error_when_a_prescription_drug_has_no_ref(self, capsys, services, drug_service):
        drug = drug_service.add_drug(name="Amoxicillin", price=150, stock=10, requires_prescription=True)
        args = SimpleNamespace(drug_id=drug.id, prescription_ref=None)

        _place_order(args=args, services=services)

        output = capsys.readouterr().out
        assert "Error" in output

    def test_shows_an_otc_advisory_after_repeated_purchases(self, capsys, services, drug_service):
        drug = drug_service.add_drug(
            name="Panadol", price=50, stock=20, requires_prescription=False, category="analgesic"
        )
        args = SimpleNamespace(drug_id=drug.id, prescription_ref=None)

        
        _place_order(args=args, services=services)
        _place_order(args=args, services=services)
        capsys.readouterr()  
        _place_order(args=args, services=services)

        output = capsys.readouterr().out
        assert "Advisory" in output
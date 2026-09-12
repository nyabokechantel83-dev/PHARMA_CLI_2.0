import pytest

from cli import menu
from main import main
from models import drug as drug_model
from models import order as order_model
from models import prescription as prescription_model
from models import user as user_model
from utils import auth


@pytest.fixture(name="answer_with")
def answer_with_fixture(monkeypatch):

    def set_answers(typed, passwords=("secret123",) * 6):
        typed_queue = list(typed)
        password_queue = list(passwords)

        def fake_input(prompt=""):
            del prompt
            if not typed_queue:
                raise EOFError
            return typed_queue.pop(0)

        def fake_getpass(prompt=""):
            del prompt
            if not password_queue:
                raise EOFError
            return password_queue.pop(0)

        monkeypatch.setattr("builtins.input", fake_input)
        monkeypatch.setattr(menu.getpass, "getpass", fake_getpass)

    return set_answers


def test_quitting_straight_away_works(answer_with):
    answer_with(["3"])         
    assert main([]) == 0


def test_running_main_with_no_arguments_opens_the_menu(answer_with, capsys):
    answer_with(["3"])

    main([])

    assert "=== Pharma-CLI ===" in capsys.readouterr().out


def test_a_typing_mistake_asks_again_instead_of_crashing(answer_with, capsys):
    answer_with(["banana", "99", "3"])

    assert main([]) == 0

    printed = capsys.readouterr().out
    assert "Please type the number" in printed
    assert "between 1 and 3" in printed


def test_registering_through_the_menu_creates_an_account(answer_with):
    answer_with(["1", "Pam Pharm", "pam@mail.com", "2"])

    main([])

    created = user_model.find_by_email("pam@mail.com")
    assert created is not None
    assert created.role == "pharmacist"


def test_a_password_typed_twice_differently_is_refused(answer_with, capsys):
    answer_with(
        ["1", "Pam Pharm", "pam@mail.com", "2"],
        passwords=["secret123", "secret124", "secret123", "secret123"],
    )

    main([])

    assert "did not match" in capsys.readouterr().out
    assert user_model.find_by_email("pam@mail.com") is not None


def test_logging_in_through_the_menu(answer_with, pharmacist_user):
    answer_with(["2", "pharmacist@wrong.com"])   

    main([])

    assert auth.current_user() is None

    answer_with(["2", pharmacist_user.email])
    main([])

    assert auth.current_user().id == pharmacist_user.id


def test_a_pharmacist_adds_a_drug_through_the_menu(answer_with, pharmacist_user):
    auth.login(pharmacist_user.email, "secret123")

    answer_with(["1", "Panadol", "50", "20", "painkiller", "n"])

    main([])

    drugs = drug_model.load_drugs()
    assert len(drugs) == 1
    assert drugs[0].name == "Panadol"
    assert drugs[0].price == 50.0
    assert drugs[0].requires_rx is False


def test_a_doctor_writes_a_prescription_through_the_menu(answer_with, doctor_user):
    auth.login(doctor_user.email, "secret123")
   
    answer_with(["1", "Ann Customer", "Amoxicillin", ""])

    main([])

    prescriptions = prescription_model.load_prescriptions()
    assert len(prescriptions) == 1
    assert prescriptions[0].ref == "RX-0001"
    assert prescriptions[0].patient_name == "Ann Customer"


def test_a_customer_orders_through_the_menu(answer_with, pharmacist_user, customer_user):
    auth.login(pharmacist_user.email, "secret123")
    main(["add-drug", "--name", "Panadol", "--price", "50", "--stock", "20"])

    auth.login(customer_user.email, "secret123")
    
    answer_with(["2", "1", ""])

    main([])

    orders = order_model.load_orders()
    assert len(orders) == 1
    assert orders[0].status == order_model.STATUS_COMPLETED
    assert drug_model.find_by_id(1).stock == 19


def test_the_menu_reports_a_mistake_and_keeps_going(answer_with, customer_user, capsys):
    auth.login(customer_user.email, "secret123")
   
    answer_with(["2", "42", "", "5"])

    assert main([]) == 0

    assert "There is no drug with id 42" in capsys.readouterr().out


def test_a_pharmacist_approves_a_claim_through_the_menu(
    answer_with, pharmacist_user, doctor_user, customer_user
):
    auth.login(pharmacist_user.email, "secret123")
    main(["add-drug", "--name", "Amoxicillin", "--price", "350",
          "--stock", "5", "--requires-rx"])

    auth.login(doctor_user.email, "secret123")
    main(["issue-prescription", "--patient-name", customer_user.name,
          "--drug-name", "Amoxicillin"])

    auth.login(customer_user.email, "secret123")
    main(["order", "--drug-id", "1", "--prescription-ref", "RX-0001"])

    auth.login(pharmacist_user.email, "secret123")
   
    answer_with(["4", "y", "1", "y"])

    main([])

    assert order_model.find_by_id(1).status == order_model.STATUS_APPROVED
    assert drug_model.find_by_id(1).stock == 4
    assert prescription_model.find_by_ref("RX-0001").used is True


def test_logging_out_through_the_menu(answer_with, customer_user):
    auth.login(customer_user.email, "secret123")
    answer_with(["4"])       

    main([])

    assert auth.current_user() is None



def test_an_empty_answer_is_asked_again(answer_with, capsys):
    answer_with(["", "   ", "Panadol"])

    assert menu.ask_text("Drug name") == "Panadol"
    assert "Please type something" in capsys.readouterr().out


def test_pressing_enter_takes_the_default(answer_with):
    answer_with([""])

    assert menu.ask_text("Category", default="general") == "general"


def test_optional_text_is_none_when_left_blank(answer_with):
    answer_with([""])

    assert menu.ask_optional_text("Prescription reference") is None


def test_words_are_refused_where_a_whole_number_is_wanted(answer_with, capsys):
    answer_with(["ten", "3.5", "10"])

    assert menu.ask_whole_number("Stock") == 10
    assert "Please type a whole number" in capsys.readouterr().out


def test_a_whole_number_can_have_a_default(answer_with):
    answer_with([""])

    assert menu.ask_whole_number("Days valid", default=30) == 30


def test_words_are_refused_where_a_price_is_wanted(answer_with, capsys):
    answer_with(["free", "49.99"])

    assert menu.ask_decimal("Price") == 49.99
    assert "Please type a number" in capsys.readouterr().out


def test_yes_and_no_are_understood_in_long_and_short_form(answer_with):
    answer_with(["yes"])
    assert menu.ask_yes_no("Sure?") is True

    answer_with(["N"])
    assert menu.ask_yes_no("Sure?") is False


def test_anything_other_than_yes_or_no_is_asked_again(answer_with, capsys):
    answer_with(["maybe", "y"])

    assert menu.ask_yes_no("Sure?") is True
    assert "Please answer y or n" in capsys.readouterr().out


def test_every_pharmacist_menu_option_runs(answer_with, pharmacist_user, capsys):
    auth.login(pharmacist_user.email, "secret123")
    main(["add-drug", "--name", "Panadol", "--price", "50", "--stock", "2"])
    capsys.readouterr()

   
    answer_with(["3", "2", "1", "8", "5", "6"])

    assert main([]) == 0

    printed = capsys.readouterr().out
    assert "Panadol" in printed
    assert "now has 10 units" in printed
    assert "Nothing to flag" in printed
    assert "Logged out" in printed


def test_every_customer_menu_option_runs(answer_with, pharmacist_user, customer_user, capsys):
    auth.login(pharmacist_user.email, "secret123")
    main(["add-drug", "--name", "Panadol", "--price", "50", "--stock", "5"])

    auth.login(customer_user.email, "secret123")
    capsys.readouterr()

  
    answer_with(["1", "3", "5"])

    assert main([]) == 0

    printed = capsys.readouterr().out
    assert "Panadol" in printed
    assert "not placed any orders" in printed


def test_every_doctor_menu_option_runs(answer_with, doctor_user, capsys):
    auth.login(doctor_user.email, "secret123")
    capsys.readouterr()

   
    answer_with(["2", "4"])

    assert main([]) == 0
    assert "No prescriptions found" in capsys.readouterr().out


def test_reviewing_claims_without_deciding(answer_with, pharmacist_user, capsys):
    auth.login(pharmacist_user.email, "secret123")
    capsys.readouterr()

    answer_with(["4", "n", "7"])

    assert main([]) == 0
    assert "No claims are waiting" in capsys.readouterr().out


def test_a_pharmacist_can_reject_through_the_menu(
    answer_with, pharmacist_user, customer_user
):
    auth.login(pharmacist_user.email, "secret123")
    main(["add-drug", "--name", "Diazepam", "--price", "400",
          "--stock", "3", "--requires-rx"])

    auth.login(customer_user.email, "secret123")
    main(["order", "--drug-id", "1", "--prescription-ref", "RX-0404"])

    auth.login(pharmacist_user.email, "secret123")
   
    answer_with(["4", "y", "1", "n"])

    main([])

    assert order_model.find_by_id(1).status == order_model.STATUS_REJECTED
    assert drug_model.find_by_id(1).stock == 3


def test_pressing_ctrl_c_leaves_politely(answer_with, capsys, monkeypatch):
    def interrupt(prompt=""):
        del prompt
        raise KeyboardInterrupt

    answer_with([])
    monkeypatch.setattr("builtins.input", interrupt)

    assert main([]) == 0
    assert "Goodbye" in capsys.readouterr().out
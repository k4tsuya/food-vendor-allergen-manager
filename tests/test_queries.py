from src.product_management.models import Item, Allergen, MeatType
from src.product_management.queries import (
    list_items,
    list_allergens,
    get_gluten_free_items,
    pdf_list_items,
)


def test_list_items_returns_all_items(db_session):
    db_session.add(Item(name="Frikandel"))
    db_session.add(Item(name="Kroket"))
    db_session.commit()

    result = list_items(db_session)

    assert len(result) == 2


def test_list_allergens_returns_sorted_by_description(db_session):
    db_session.add(Allergen(code="soy", description_en="Soy", description_nl="Soja"))
    db_session.add(Allergen(code="gluten", description_en="Gluten", description_nl="Gluten"))
    db_session.commit()

    result = list_allergens(db_session)

    assert [a.description_en for a in result] == ["Gluten", "Soy"]


def test_get_gluten_free_items_excludes_gluten(db_session):
    gluten = Allergen(code="gluten", description_en="Gluten", description_nl="Gluten")
    milk = Allergen(code="milk", description_en="Milk", description_nl="Melk")

    kroket = Item(name="Kroket", allergens=[gluten, milk])
    fishstick = Item(name="Fishstick", allergens=[milk])

    db_session.add_all([kroket, fishstick])
    db_session.commit()

    result = get_gluten_free_items(db_session)

    assert [i.name for i in result] == ["Fishstick"]


def test_pdf_list_items_returns_correct_shape(db_session):
    gluten = Allergen(code="gluten", description_en="Gluten", description_nl="Gluten")
    item = Item(name="Bread", allergens=[gluten])

    db_session.add(item)
    db_session.commit()

    result = pdf_list_items(db_session)

    assert len(result) == 1
    assert result[0].name == "Bread"
    assert result[0].allergens == ["gluten"]


def test_list_items_respects_limit_and_offset(db_session):
    for name in ["Frikandel", "Kroket", "Bread", "Fishstick"]:
        db_session.add(Item(name=name))
    db_session.commit()

    result = list_items(db_session, limit=2, offset=1)

    assert len(result) == 2
    

from src.product_management.models import MeatType


def test_list_items_search_filters_by_name(db_session):
    db_session.add(Item(name="Frikandel"))
    db_session.add(Item(name="Kroket"))
    db_session.commit()

    result = list_items(db_session, search="fri")

    assert [i.name for i in result] == ["Frikandel"]


def test_list_items_exclude_allergens_filters_correctly(db_session):
    gluten = Allergen(code="gluten", description_en="Gluten", description_nl="Gluten")
    milk = Allergen(code="milk", description_en="Milk", description_nl="Melk")

    bread = Item(name="Bread", allergens=[gluten])
    fishstick = Item(name="Fishstick", allergens=[milk])
    plain = Item(name="Plain")

    db_session.add_all([bread, fishstick, plain])
    db_session.commit()

    result = list_items(db_session, exclude_allergens=["gluten"])

    names = [i.name for i in result]
    assert "Bread" not in names
    assert "Fishstick" in names
    assert "Plain" in names


def test_list_items_meat_types_filters_correctly(db_session):
    pork = MeatType(code="pork", description_en="Pork", description_nl="Varkensvlees")
    beef = MeatType(code="beef", description_en="Beef", description_nl="Rundvlees")

    frikandel = Item(name="Frikandel", meat_types=[pork, beef])
    veggie = Item(name="Veggie Bite")

    db_session.add_all([frikandel, veggie])
    db_session.commit()

    result = list_items(db_session, meat_types=["pork"])

    names = [i.name for i in result]
    assert "Frikandel" in names
    assert "Veggie Bite" not in names
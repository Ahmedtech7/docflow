"""Area 2: inventory summaries (count_by and show_inventory).

الهدف: نتأكد إن الملخص (عدد المستندات حسب النوع والقسم) يُحسب ويُطبع صح.
وش نسوي: نختبر count_by على بيانات سليمة وعلى قائمة فاضية، ونتأكد من شكل
المخرجات حرفياً. ولو فيه سجل خربان، لازم يذكر رقمه واسم الحقل وما يطبع مجاميع ناقصة.
"""

import pytest

from inventory import count_by, show_inventory


def test_count_by_type_and_department(make_doc):
    docs = [
        make_doc(document_type="txt", department="HR"),
        make_doc(document_type="md", department="HR"),
        make_doc(document_type="txt", department="IT"),
    ]
    assert count_by(docs, "document_type") == {"txt": 2, "md": 1}
    assert count_by(docs, "department") == {"HR": 2, "IT": 1}


def test_count_by_empty_list_is_empty():
    assert count_by([], "department") == {}


def test_show_inventory_prints_totals_sorted(make_doc, capsys):
    show_inventory([make_doc(department="IT"), make_doc(department="Finance", document_type="md")])
    assert capsys.readouterr().out == (
        "DocFlow - Document Inventory\n"
        "Total documents: 2\n"
        "\nBy type:\n  md: 1\n  txt: 1\n"
        "\nBy department:\n  Finance: 1\n  IT: 1\n"
    )


def test_show_inventory_empty(capsys):
    show_inventory([])
    assert "Total documents: 0" in capsys.readouterr().out


# Documented policy (Task 2.1, bug C): the plain summary fails cleanly.
@pytest.mark.parametrize(
    "bad",
    [
        {"department": None},
        {"department": ""},
        {"department": "   "},
        {"document_type": 5},
    ],
)
def test_malformed_field_names_record_and_field(make_doc, bad):
    with pytest.raises(ValueError, match=r"index 1 .*'(department|document_type)'"):
        show_inventory([make_doc(), make_doc(**bad)])


def test_missing_field_names_record_and_field(make_doc):
    doc = make_doc()
    del doc["department"]
    with pytest.raises(ValueError, match=r"index 0 .*'department'"):
        count_by([doc], "department")


def test_non_object_record_is_reported(make_doc):
    with pytest.raises(ValueError, match="index 1"):
        count_by([make_doc(), "not-an-object"], "department")


def test_malformed_record_prints_no_partial_totals(make_doc, capsys):
    with pytest.raises(ValueError):
        show_inventory([make_doc(), make_doc(department=None)])
    assert capsys.readouterr().out == ""

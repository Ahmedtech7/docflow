"""Area 1: inventory loading.

الهدف: نتأكد إن load_inventory يقرأ ملف JSON صح، ويرفض الملفات الغلط.
وش نسوي: نجرب ملف سليم، وملف فاضي []، وملف غير موجود، وملف JSON خربان،
وملف مو قائمة (مثل {} أو نص أو رقم). كل حالة غلط لازم تطلع خطأ واضح.
"""

import json

import pytest

from inventory import load_inventory


def test_valid_array_is_returned_unchanged(write_json, make_doc):
    docs = [make_doc(), make_doc(id="DOC-002")]
    assert load_inventory(write_json(docs)) == docs


def test_empty_array_returns_empty_list(write_json):
    assert load_inventory(write_json([])) == []


def test_missing_file_raises_os_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_inventory(tmp_path / "missing.json")


def test_malformed_json_raises_value_error(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ invalid", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_inventory(path)


@pytest.mark.parametrize("data", [{}, {"documents": []}, "text", 5, None])
def test_non_array_top_level_is_rejected(write_json, data):
    with pytest.raises(ValueError, match="JSON must contain an array"):
        load_inventory(write_json(data))

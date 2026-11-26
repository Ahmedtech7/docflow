"""Area 4: duplicate ID handling in validate_inventory.

# الهدف: نتأكد إن الـ ID المكرر ينرفض بشكل صحيح.
# وش نسوي: DOC-001 و doc-001 و " Doc-001 " تعتبر نفس الـ ID. أول مستند سليم يفوز،
# والمستند المرفوض ما يحجز الـ ID. ومجموع المقبول + المرفوض = عدد السجلات.
"""

from inventory import validate_inventory


def test_duplicate_ids_are_case_and_space_insensitive(make_doc):
    docs = [make_doc(id="DOC-001"), make_doc(id="doc-001"), make_doc(id="  Doc-001 ")]
    accepted, rejected = validate_inventory(docs)
    assert accepted == [docs[0]]
    assert rejected == [
        (1, "doc-001", ["Duplicate document ID"]),
        (2, "doc-001", ["Duplicate document ID"]),
    ]


def test_first_valid_occurrence_wins(make_doc):
    docs = [make_doc(id="A"), make_doc(id="B"), make_doc(id="a")]
    accepted, rejected = validate_inventory(docs)
    assert [d["id"] for d in accepted] == ["A", "B"]
    assert [index for index, _, _ in rejected] == [2]


def test_invalid_earlier_record_does_not_block_later_valid_one(make_doc):
    # Only accepted IDs count, so a rejected DOC-001 does not make the next one a duplicate.
    docs = [make_doc(id="DOC-001", size_kb=0), make_doc(id="DOC-001")]
    accepted, rejected = validate_inventory(docs)
    assert accepted == [docs[1]]
    assert rejected == [(0, "doc-001", ["Size must be between 0 and 5120 KB"])]


def test_duplicate_reason_is_added_to_other_errors(make_doc):
    docs = [make_doc(id="X"), make_doc(id="x", size_kb=-1)]
    _, rejected = validate_inventory(docs)
    assert rejected == [(1, "x", ["Size must be between 0 and 5120 KB", "Duplicate document ID"])]


def test_totals_add_up(make_doc):
    docs = [
        make_doc(id="A"),
        make_doc(id="a"),
        make_doc(id="B", document_type="pdf"),
        make_doc(id="C"),
        "bad",
    ]
    accepted, rejected = validate_inventory(docs)
    assert (len(accepted), len(rejected)) == (2, 3)
    assert len(accepted) + len(rejected) == len(docs)


def test_record_without_usable_id_has_none_id(make_doc):
    docs = [make_doc(id=""), "not-an-object"]
    _, rejected = validate_inventory(docs)
    assert [(index, doc_id) for index, doc_id, _ in rejected] == [(0, None), (1, None)]
